"""
IronWall Antivirus - Cloud Threat Intelligence Module
Check file hashes against VirusTotal and other remote threat databases
"""

import os
import hashlib
import json
import requests
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import urllib.parse

class CloudThreatIntelligence:
    def __init__(self):
        # API keys (should be set as environment variables)
        self.virustotal_api_key = os.environ.get('VT_API_KEY')
        self.hybrid_analysis_api_key = os.environ.get('HA_API_KEY')
        self.malware_bazaar_api_key = os.environ.get('MB_API_KEY')
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Rate limiting
        self.rate_limits = {
            'virustotal': {'requests_per_minute': 4, 'last_request': 0},
            'hybrid_analysis': {'requests_per_minute': 10, 'last_request': 0},
            'malware_bazaar': {'requests_per_minute': 30, 'last_request': 0}
        }
        
        # Threat intelligence sources
        self.intelligence_sources = {
            'virustotal': {
                'name': 'VirusTotal',
                'url': 'https://www.virustotal.com/vtapi/v2/file/report',
                'enabled': bool(self.virustotal_api_key),
                'description': 'Multi-engine antivirus scanning service'
            },
            'hybrid_analysis': {
                'name': 'Hybrid Analysis',
                'url': 'https://www.hybrid-analysis.com/api/v2/search/hash',
                'enabled': bool(self.hybrid_analysis_api_key),
                'description': 'Advanced malware analysis platform'
            },
            'malware_bazaar': {
                'name': 'MalwareBazaar',
                'url': 'https://bazaar.abuse.ch/api/v1/',
                'enabled': True,  # No API key required
                'description': 'Malware sample sharing platform'
            },
            'urlhaus': {
                'name': 'URLhaus',
                'url': 'https://urlhaus.abuse.ch/api/v1/',
                'enabled': True,  # No API key required
                'description': 'Malicious URL database'
            },
            'threatfox': {
                'name': 'ThreatFox',
                'url': 'https://threatfox.abuse.ch/api/v1/',
                'enabled': True,  # No API key required
                'description': 'Malware IOC database'
            }
        }
        
        # Initialize cache cleanup thread
        self._start_cache_cleanup()
    
    def _start_cache_cleanup(self):
        """Start background thread to clean up expired cache entries"""
        def cleanup_loop():
            while True:
                try:
                    self._cleanup_cache()
                    time.sleep(300)  # Clean up every 5 minutes
                except Exception as e:
                    print(f"Cloud Intelligence: Cache cleanup error: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def _rate_limit_check(self, source: str) -> bool:
        """Check if we can make a request to the specified source"""
        if source not in self.rate_limits:
            return True
        
        limit_info = self.rate_limits[source]
        current_time = time.time()
        
        # Check if enough time has passed since last request
        if current_time - limit_info['last_request'] < (60 / limit_info['requests_per_minute']):
            return False
        
        limit_info['last_request'] = current_time
        return True
    
    def check_file_hash(self, file_hash: str, sources: List[str] = None) -> Dict[str, Any]:
        """Check file hash against multiple threat intelligence sources"""
        if sources is None:
            sources = ['virustotal', 'malware_bazaar', 'threatfox']
        
        # Check cache first
        cache_key = f"{file_hash}_{'_'.join(sorted(sources))}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
        
        # Initialize result
        result = {
            'file_hash': file_hash,
            'check_timestamp': datetime.now().isoformat(),
            'sources_checked': [],
            'overall_verdict': 'Unknown',
            'detection_ratio': 0.0,
            'total_engines': 0,
            'positive_engines': 0,
            'source_results': {},
            'threat_families': [],
            'tags': [],
            'first_seen': None,
            'last_seen': None
        }
        
        # Check each source
        for source in sources:
            if source in self.intelligence_sources and self.intelligence_sources[source]['enabled']:
                if self._rate_limit_check(source):
                    try:
                        source_result = self._check_source(file_hash, source)
                        result['source_results'][source] = source_result
                        result['sources_checked'].append(source)
                        
                        # Update overall statistics
                        self._update_overall_stats(result, source_result)
                        
                    except Exception as e:
                        result['source_results'][source] = {
                            'error': str(e),
                            'status': 'error'
                        }
                else:
                    result['source_results'][source] = {
                        'error': 'Rate limit exceeded',
                        'status': 'rate_limited'
                    }
        
        # Determine overall verdict
        result['overall_verdict'] = self._determine_overall_verdict(result)
        
        # Cache the result
        self.cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result
    
    def _check_source(self, file_hash: str, source: str) -> Dict[str, Any]:
        """Check file hash against a specific source"""
        if source == 'virustotal':
            return self._check_virustotal(file_hash)
        elif source == 'hybrid_analysis':
            return self._check_hybrid_analysis(file_hash)
        elif source == 'malware_bazaar':
            return self._check_malware_bazaar(file_hash)
        elif source == 'threatfox':
            return self._check_threatfox(file_hash)
        else:
            return {'error': f'Unknown source: {source}', 'status': 'error'}
    
    def _check_virustotal(self, file_hash: str) -> Dict[str, Any]:
        """Check file hash against VirusTotal"""
        try:
            url = self.intelligence_sources['virustotal']['url']
            params = {
                'apikey': self.virustotal_api_key,
                'resource': file_hash
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('response_code') == 1:
                    positives = data.get('positives', 0)
                    total = data.get('total', 0)
                    
                    return {
                        'status': 'success',
                        'detection_ratio': positives / total if total > 0 else 0,
                        'positive_engines': positives,
                        'total_engines': total,
                        'scan_date': data.get('scan_date'),
                        'permalink': data.get('permalink'),
                        'scans': data.get('scans', {}),
                        'sha256': data.get('sha256'),
                        'sha1': data.get('sha1'),
                        'md5': data.get('md5'),
                        'file_size': data.get('file_size'),
                        'file_type': data.get('file_type'),
                        'tags': data.get('tags', [])
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': 'File not found in VirusTotal database'
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_hybrid_analysis(self, file_hash: str) -> Dict[str, Any]:
        """Check file hash against Hybrid Analysis"""
        try:
            url = self.intelligence_sources['hybrid_analysis']['url']
            headers = {
                'api-key': self.hybrid_analysis_api_key,
                'user-agent': 'IronWall Antivirus'
            }
            data = {
                'hash': file_hash
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('count', 0) > 0:
                    sample = data['data'][0]
                    
                    return {
                        'status': 'success',
                        'verdict': sample.get('verdict'),
                        'threat_score': sample.get('threat_score'),
                        'threat_level': sample.get('threat_level'),
                        'analysis_start_time': sample.get('analysis_start_time'),
                        'analysis_end_time': sample.get('analysis_end_time'),
                        'file_type': sample.get('file_type'),
                        'file_size': sample.get('file_size'),
                        'tags': sample.get('tags', [])
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': 'File not found in Hybrid Analysis database'
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_malware_bazaar(self, file_hash: str) -> Dict[str, Any]:
        """Check file hash against MalwareBazaar"""
        try:
            url = self.intelligence_sources['malware_bazaar']['url']
            data = {
                'query': 'get_info',
                'hash': file_hash
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('query_status') == 'ok':
                    return {
                        'status': 'success',
                        'file_name': data.get('data', {}).get('file_name'),
                        'file_type': data.get('data', {}).get('file_type'),
                        'file_size': data.get('data', {}).get('file_size'),
                        'signature': data.get('data', {}).get('signature'),
                        'tags': data.get('data', {}).get('tags', []),
                        'first_seen': data.get('data', {}).get('first_seen'),
                        'last_seen': data.get('data', {}).get('last_seen')
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': 'File not found in MalwareBazaar database'
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_threatfox(self, file_hash: str) -> Dict[str, Any]:
        """Check file hash against ThreatFox"""
        try:
            url = self.intelligence_sources['threatfox']['url']
            data = {
                'query': 'search_ioc',
                'search_term': file_hash
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('query_status') == 'ok' and data.get('data'):
                    ioc_data = data['data'][0]
                    
                    return {
                        'status': 'success',
                        'ioc_type': ioc_data.get('ioc_type'),
                        'threat_type': ioc_data.get('threat_type'),
                        'malware': ioc_data.get('malware'),
                        'malware_alias': ioc_data.get('malware_alias'),
                        'malware_printable': ioc_data.get('malware_printable'),
                        'first_seen': ioc_data.get('first_seen'),
                        'last_seen': ioc_data.get('last_seen'),
                        'confidence_level': ioc_data.get('confidence_level')
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': 'File not found in ThreatFox database'
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _update_overall_stats(self, result: Dict[str, Any], source_result: Dict[str, Any]):
        """Update overall statistics from source results"""
        if source_result.get('status') == 'success':
            # Update detection ratio
            if 'detection_ratio' in source_result:
                result['detection_ratio'] = max(result['detection_ratio'], source_result['detection_ratio'])
            
            # Update engine counts
            if 'positive_engines' in source_result and 'total_engines' in source_result:
                result['positive_engines'] += source_result['positive_engines']
                result['total_engines'] += source_result['total_engines']
            
            # Update threat families
            if 'malware' in source_result:
                result['threat_families'].append(source_result['malware'])
            
            # Update tags
            if 'tags' in source_result:
                result['tags'].extend(source_result['tags'])
            
            # Update first/last seen dates
            if 'first_seen' in source_result:
                if result['first_seen'] is None or source_result['first_seen'] < result['first_seen']:
                    result['first_seen'] = source_result['first_seen']
            
            if 'last_seen' in source_result:
                if result['last_seen'] is None or source_result['last_seen'] > result['last_seen']:
                    result['last_seen'] = source_result['last_seen']
    
    def _determine_overall_verdict(self, result: Dict[str, Any]) -> str:
        """Determine overall verdict based on all source results"""
        if result['detection_ratio'] >= 0.5:
            return 'Malicious'
        elif result['detection_ratio'] >= 0.1:
            return 'Suspicious'
        elif result['positive_engines'] > 0:
            return 'Low Risk'
        else:
            return 'Clean'
    
    def check_url(self, url: str) -> Dict[str, Any]:
        """Check URL against threat intelligence sources"""
        try:
            # Check URLhaus
            urlhaus_result = self._check_urlhaus(url)
            
            result = {
                'url': url,
                'check_timestamp': datetime.now().isoformat(),
                'overall_verdict': 'Unknown',
                'source_results': {
                    'urlhaus': urlhaus_result
                }
            }
            
            # Determine overall verdict
            if urlhaus_result.get('status') == 'success':
                if urlhaus_result.get('threat') == 'malicious':
                    result['overall_verdict'] = 'Malicious'
                elif urlhaus_result.get('threat') == 'suspicious':
                    result['overall_verdict'] = 'Suspicious'
                else:
                    result['overall_verdict'] = 'Clean'
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'check_timestamp': datetime.now().isoformat(),
                'overall_verdict': 'Unknown',
                'error': str(e)
            }
    
    def _check_urlhaus(self, url: str) -> Dict[str, Any]:
        """Check URL against URLhaus"""
        try:
            urlhaus_url = self.intelligence_sources['urlhaus']['url']
            data = {
                'url': url
            }
            
            response = requests.post(urlhaus_url, data=data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('query_status') == 'ok':
                    return {
                        'status': 'success',
                        'threat': data.get('threat'),
                        'tags': data.get('tags', []),
                        'date_added': data.get('date_added'),
                        'url_status': data.get('url_status')
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': 'URL not found in URLhaus database'
                    }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_available_sources(self) -> Dict[str, Any]:
        """Get information about available threat intelligence sources"""
        return {
            'sources': self.intelligence_sources,
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'rate_limits': self.rate_limits,
            'last_update': datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'last_cleanup': datetime.now().isoformat()
        } 