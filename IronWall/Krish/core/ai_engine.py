"""
IronWall Antivirus - AI/ML Behavioral Engine
Lightweight machine learning model for threat detection and behavioral analysis
"""

import os
import hashlib
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import threading
import time
from datetime import datetime
import requests
import re

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: scikit-learn not available. AI features will be limited.")

class AIBehavioralEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), '..', 'models', 'threat_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl')
        self.vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'vectorizer.pkl')
        
        # Initialize models
        self.threat_classifier = None
        self.anomaly_detector = None
        self.text_vectorizer = None
        self.scaler = None
        
        # Feature extraction cache
        self.feature_cache = {}
        self.cache_size = 1000
        
        # Threat intelligence cache
        self.threat_intel_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Load or initialize models
        self._initialize_models()
        
        # Behavioral patterns
        self.suspicious_behaviors = {
            'file_operations': [
                'mass_file_creation', 'mass_file_deletion', 'file_encryption',
                'registry_modification', 'startup_modification'
            ],
            'network_activity': [
                'unusual_connections', 'data_exfiltration', 'command_control',
                'dns_tunneling', 'port_scanning'
            ],
            'process_activity': [
                'process_injection', 'code_injection', 'privilege_escalation',
                'persistence_mechanism', 'anti_debugging'
            ],
            'system_activity': [
                'service_manipulation', 'scheduled_task_creation', 'user_creation',
                'group_modification', 'audit_disable'
            ]
        }
    
    def _initialize_models(self):
        """Initialize or load ML models"""
        try:
            # Create models directory if it doesn't exist
            models_dir = os.path.dirname(self.model_path)
            os.makedirs(models_dir, exist_ok=True)
            
            if os.path.exists(self.model_path) and HAS_SKLEARN:
                # Load existing models
                with open(self.model_path, 'rb') as f:
                    self.threat_classifier = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.text_vectorizer = pickle.load(f)
                
                # Initialize anomaly detector
                self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
                
                print("AI Engine: Models loaded successfully")
            else:
                # Initialize new models
                self._create_initial_models()
                print("AI Engine: New models initialized")
                
        except Exception as e:
            print(f"AI Engine: Error initializing models: {e}")
            self._create_fallback_models()
    
    def _create_initial_models(self):
        """Create initial ML models with basic training data"""
        if not HAS_SKLEARN:
            return
            
        # Create basic training data
        training_data = self._generate_training_data()
        
        # Initialize models
        self.threat_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        
        # Train models
        if training_data['features'].shape[0] > 0:
            # Scale features
            scaled_features = self.scaler.fit_transform(training_data['features'])
            
            # Train threat classifier
            self.threat_classifier.fit(scaled_features, training_data['labels'])
            
            # Train anomaly detector
            self.anomaly_detector.fit(scaled_features)
            
            # Train text vectorizer
            if training_data['texts']:
                self.text_vectorizer.fit(training_data['texts'])
            
            # Save models
            self._save_models()
    
    def _create_fallback_models(self):
        """Create fallback models when sklearn is not available"""
        self.threat_classifier = None
        self.anomaly_detector = None
        self.text_vectorizer = None
        self.scaler = None
    
    def _generate_training_data(self) -> Dict[str, Any]:
        """Generate basic training data for initial model training"""
        features = []
        labels = []
        texts = []
        
        # Generate benign file features
        for i in range(100):
            # Benign file features
            benign_features = [
                np.random.normal(0.3, 0.1),  # entropy
                np.random.normal(0.1, 0.05),  # suspicious_patterns
                np.random.normal(0.05, 0.02),  # encoded_content
                np.random.normal(0.02, 0.01),  # network_activity
                np.random.normal(0.1, 0.05),  # file_size_score
                np.random.normal(0.05, 0.02),  # extension_risk
                np.random.normal(0.02, 0.01),  # location_risk
                np.random.normal(0.1, 0.05),  # age_score
            ]
            features.append(benign_features)
            labels.append(0)  # Benign
            texts.append("normal file content")
        
        # Generate malicious file features
        for i in range(50):
            # Malicious file features
            malicious_features = [
                np.random.normal(0.8, 0.1),  # entropy
                np.random.normal(0.8, 0.1),  # suspicious_patterns
                np.random.normal(0.7, 0.2),  # encoded_content
                np.random.normal(0.6, 0.2),  # network_activity
                np.random.normal(0.3, 0.1),  # file_size_score
                np.random.normal(0.8, 0.1),  # extension_risk
                np.random.normal(0.7, 0.2),  # location_risk
                np.random.normal(0.2, 0.1),  # age_score
            ]
            features.append(malicious_features)
            labels.append(1)  # Malicious
            texts.append("malicious content patterns")
        
        return {
            'features': np.array(features),
            'labels': np.array(labels),
            'texts': texts
        }
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            if self.threat_classifier:
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.threat_classifier, f)
            if self.scaler:
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
            if self.text_vectorizer:
                with open(self.vectorizer_path, 'wb') as f:
                    pickle.dump(self.text_vectorizer, f)
        except Exception as e:
            print(f"AI Engine: Error saving models: {e}")
    
    def extract_features(self, file_path: str, file_content: str = None) -> Dict[str, float]:
        """Extract features from a file for ML analysis"""
        try:
            # Check cache first
            file_hash = self._calculate_file_hash(file_path)
            if file_hash in self.feature_cache:
                return self.feature_cache[file_hash]
            
            features = {}
            
            # Basic file features
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)
            
            # Entropy calculation
            features['entropy'] = self._calculate_entropy(file_path)
            
            # Suspicious patterns
            features['suspicious_patterns'] = self._detect_suspicious_patterns(file_path, file_content)
            
            # Encoded content detection
            features['encoded_content'] = self._detect_encoded_content(file_path, file_content)
            
            # Network activity indicators
            features['network_activity'] = self._detect_network_activity(file_path, file_content)
            
            # File size risk score
            features['file_size_score'] = self._calculate_size_risk(file_size)
            
            # Extension risk score
            features['extension_risk'] = self._calculate_extension_risk(file_ext)
            
            # Location risk score
            features['location_risk'] = self._calculate_location_risk(file_path)
            
            # File age score
            features['age_score'] = self._calculate_age_risk(file_path)
            
            # Cache the features
            if len(self.feature_cache) < self.cache_size:
                self.feature_cache[file_hash] = features
            
            return features
            
        except Exception as e:
            print(f"AI Engine: Error extracting features: {e}")
            return self._get_default_features()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return hashlib.md5(file_path.encode()).hexdigest()
    
    def _calculate_entropy(self, file_path: str) -> float:
        """Calculate Shannon entropy of file content"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(8192)  # Read first 8KB for entropy calculation
            
            if not data:
                return 0.0
            
            # Calculate byte frequency
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
            
            # Calculate entropy
            entropy = 0.0
            data_len = len(data)
            for count in byte_counts:
                if count > 0:
                    probability = count / data_len
                    entropy -= probability * np.log2(probability)
            
            return entropy / 8.0  # Normalize to 0-1 range
            
        except Exception:
            return 0.5
    
    def _detect_suspicious_patterns(self, file_path: str, content: str = None) -> float:
        """Detect suspicious patterns in file content"""
        try:
            if content is None:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)  # Read first 4KB
            
            suspicious_count = 0
            total_patterns = 0
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'del\s+\*\.\*', r'format\s+[a-z]:', r'shutdown\s+/s',
                r'powershell\s+-enc', r'cmd\.exe\s+/c', r'wget\s+',
                r'curl\s+', r'net\s+user', r'reg\s+add', r'schtasks\s+/create',
                r'base64\s+', r'certutil\s+-decode', r'rundll32\s+',
                r'CreateRemoteThread', r'VirtualAlloc', r'SetWindowsHookEx'
            ]
            
            for pattern in suspicious_patterns:
                total_patterns += 1
                if re.search(pattern, content, re.IGNORECASE):
                    suspicious_count += 1
            
            return suspicious_count / max(total_patterns, 1)
            
        except Exception:
            return 0.0
    
    def _detect_encoded_content(self, file_path: str, content: str = None) -> float:
        """Detect encoded or obfuscated content"""
        try:
            if content is None:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
            
            # Check for base64 patterns
            base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
            base64_matches = len(re.findall(base64_pattern, content))
            
            # Check for hex patterns
            hex_pattern = r'[0-9A-Fa-f]{20,}'
            hex_matches = len(re.findall(hex_pattern, content))
            
            # Check for long strings of special characters
            special_pattern = r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{10,}'
            special_matches = len(re.findall(special_pattern, content))
            
            total_indicators = base64_matches + hex_matches + special_matches
            return min(total_indicators / 10.0, 1.0)  # Normalize to 0-1
            
        except Exception:
            return 0.0
    
    def _detect_network_activity(self, file_path: str, content: str = None) -> float:
        """Detect network activity indicators"""
        try:
            if content is None:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
            
            network_indicators = [
                r'http[s]?://', r'ftp://', r'\\\\.*\\', r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
                r'wget\s+', r'curl\s+', r'net\s+use', r'ping\s+', r'nslookup\s+',
                r'connect\s+', r'socket\s+', r'bind\s+', r'listen\s+'
            ]
            
            indicator_count = 0
            for pattern in network_indicators:
                if re.search(pattern, content, re.IGNORECASE):
                    indicator_count += 1
            
            return min(indicator_count / 5.0, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_size_risk(self, file_size: int) -> float:
        """Calculate risk based on file size"""
        # Very small files (< 1KB) or very large files (> 100MB) are suspicious
        if file_size < 1024:
            return 0.7
        elif file_size > 100 * 1024 * 1024:
            return 0.6
        else:
            return 0.1
    
    def _calculate_extension_risk(self, file_ext: str) -> float:
        """Calculate risk based on file extension"""
        high_risk_extensions = {'.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.scr', '.pif', '.com'}
        medium_risk_extensions = {'.dll', '.sys', '.drv', '.ocx', '.cpl', '.msi', '.hta', '.wsf', '.reg'}
        
        if file_ext in high_risk_extensions:
            return 0.9
        elif file_ext in medium_risk_extensions:
            return 0.6
        else:
            return 0.1
    
    def _calculate_location_risk(self, file_path: str) -> float:
        """Calculate risk based on file location"""
        suspicious_locations = [
            'temp', 'tmp', 'downloads', 'desktop', 'recent',
            'startup', 'run', 'system32', 'windows'
        ]
        
        file_path_lower = file_path.lower()
        for location in suspicious_locations:
            if location in file_path_lower:
                return 0.7
        
        return 0.2
    
    def _calculate_age_risk(self, file_path: str) -> float:
        """Calculate risk based on file age"""
        try:
            file_time = os.path.getctime(file_path)
            current_time = time.time()
            age_days = (current_time - file_time) / (24 * 3600)
            
            # Very new files (< 1 day) are more suspicious
            if age_days < 1:
                return 0.8
            elif age_days < 7:
                return 0.5
            else:
                return 0.2
        except:
            return 0.5
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default features when extraction fails"""
        return {
            'entropy': 0.5,
            'suspicious_patterns': 0.0,
            'encoded_content': 0.0,
            'network_activity': 0.0,
            'file_size_score': 0.5,
            'extension_risk': 0.5,
            'location_risk': 0.5,
            'age_score': 0.5
        }
    
    def analyze_file(self, file_path: str, file_content: str = None) -> Dict[str, Any]:
        """Analyze a file and return threat assessment"""
        try:
            # Extract features
            features = self.extract_features(file_path, file_content)
            
            # Prepare feature vector
            feature_vector = np.array([
                features['entropy'],
                features['suspicious_patterns'],
                features['encoded_content'],
                features['network_activity'],
                features['file_size_score'],
                features['extension_risk'],
                features['location_risk'],
                features['age_score']
            ]).reshape(1, -1)
            
            # Get ML predictions
            threat_score = 0.0
            confidence = 0.0
            anomaly_score = 0.0
            
            if self.threat_classifier and self.scaler:
                try:
                    # Scale features
                    scaled_features = self.scaler.transform(feature_vector)
                    
                    # Get threat prediction
                    threat_prob = self.threat_classifier.predict_proba(scaled_features)[0]
                    threat_score = threat_prob[1]  # Probability of being malicious
                    
                    # Get confidence (based on prediction probability)
                    confidence = max(threat_prob[0], threat_prob[1])
                    
                    # Get anomaly score
                    if self.anomaly_detector:
                        anomaly_score = -self.anomaly_detector.score_samples(scaled_features)[0]
                        anomaly_score = max(0.0, min(1.0, anomaly_score))
                        
                except Exception as e:
                    print(f"AI Engine: Error in ML prediction: {e}")
            
            # Fallback analysis if ML models not available
            if threat_score == 0.0:
                threat_score = self._fallback_analysis(features)
                confidence = 0.6
            
            # Combine scores
            final_score = (threat_score * 0.6 + anomaly_score * 0.4)
            
            # Determine threat level
            threat_level = self._determine_threat_level(final_score)
            
            return {
                'file_path': file_path,
                'threat_score': round(final_score, 3),
                'confidence': round(confidence, 3),
                'anomaly_score': round(anomaly_score, 3),
                'threat_level': threat_level,
                'features': features,
                'analysis_timestamp': datetime.now().isoformat(),
                'ai_model_version': '1.0'
            }
            
        except Exception as e:
            print(f"AI Engine: Error analyzing file: {e}")
            return {
                'file_path': file_path,
                'threat_score': 0.5,
                'confidence': 0.0,
                'anomaly_score': 0.0,
                'threat_level': 'Unknown',
                'features': self._get_default_features(),
                'analysis_timestamp': datetime.now().isoformat(),
                'ai_model_version': '1.0',
                'error': str(e)
            }
    
    def _fallback_analysis(self, features: Dict[str, float]) -> float:
        """Fallback analysis when ML models are not available"""
        # Simple rule-based scoring
        score = 0.0
        
        # High entropy files are suspicious
        if features['entropy'] > 0.7:
            score += 0.3
        
        # Files with suspicious patterns
        if features['suspicious_patterns'] > 0.3:
            score += 0.4
        
        # Files with encoded content
        if features['encoded_content'] > 0.5:
            score += 0.3
        
        # High-risk extensions
        if features['extension_risk'] > 0.7:
            score += 0.2
        
        return min(score, 1.0)
    
    def _determine_threat_level(self, score: float) -> str:
        """Determine threat level based on score"""
        if score >= 0.8:
            return 'Critical'
        elif score >= 0.6:
            return 'High'
        elif score >= 0.4:
            return 'Medium'
        elif score >= 0.2:
            return 'Low'
        else:
            return 'Safe'
    
    def update_model(self, training_data: List[Dict[str, Any]]):
        """Update the ML model with new training data"""
        if not HAS_SKLEARN or not training_data:
            return
        
        try:
            # Extract features and labels from training data
            features = []
            labels = []
            
            for data_point in training_data:
                file_features = data_point.get('features', {})
                if file_features:
                    feature_vector = [
                        file_features.get('entropy', 0.5),
                        file_features.get('suspicious_patterns', 0.0),
                        file_features.get('encoded_content', 0.0),
                        file_features.get('network_activity', 0.0),
                        file_features.get('file_size_score', 0.5),
                        file_features.get('extension_risk', 0.5),
                        file_features.get('location_risk', 0.5),
                        file_features.get('age_score', 0.5)
                    ]
                    features.append(feature_vector)
                    labels.append(1 if data_point.get('is_malicious', False) else 0)
            
            if features and labels:
                features_array = np.array(features)
                labels_array = np.array(labels)
                
                # Retrain models
                scaled_features = self.scaler.fit_transform(features_array)
                self.threat_classifier.fit(scaled_features, labels_array)
                self.anomaly_detector.fit(scaled_features)
                
                # Save updated models
                self._save_models()
                
                print(f"AI Engine: Model updated with {len(features)} samples")
                
        except Exception as e:
            print(f"AI Engine: Error updating model: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI models"""
        return {
            'models_loaded': self.threat_classifier is not None,
            'sklearn_available': HAS_SKLEARN,
            'model_path': self.model_path,
            'cache_size': len(self.feature_cache),
            'threat_intel_cache_size': len(self.threat_intel_cache),
            'last_update': datetime.now().isoformat()
        } 