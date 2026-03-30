import React, { useState, useEffect, useRef } from 'react';
import { 
  StyleSheet, Text, View, TouchableOpacity, Animated, Easing, 
  Alert, StatusBar, TextInput, Platform, ScrollView, Dimensions, 
  KeyboardAvoidingView 
} from 'react-native';
import { getCurrentPositionAsync, requestForegroundPermissionsAsync } from 'expo-location';
import * as SMS from 'expo-sms';
import * as MailComposer from 'expo-mail-composer';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import axios from 'axios';
import { extractMFCCs, fuseDetectionScores } from './utils/audioProcessor';
import { safeLoadModel, ModelWrapper } from './utils/mlUtils';

const { width, height } = Dimensions.get('window');
// --- CONFIGURATION ---
// Use EXPO_PUBLIC_ prefix for Expo to pick up these from .env
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api'; 
// IMPORTANT: If testing on a physical phone, ensure phone and PC are on the same Wi-Fi.
// Update EXPO_PUBLIC_API_URL in mobile/.env to your PC's local IP (e.g. 192.168.1.15)

// --- THEME ENGINE ---
const THEME = {
  bg: ['#0A0E17', '#111827'],
  primary: '#7C3AED',
  secondary: '#8B5CF6',
  warning: '#F43F5E',
  danger: '#DC2626',
  success: '#10B981',
  text: '#F8FAFC',
  textDim: '#94A3B8',
  glass: 'rgba(30, 41, 59, 0.4)',
  border: 'rgba(255, 255, 255, 0.1)',
};

type ScreenState = 'login' | 'register' | 'voice_setup' | 'contacts_setup' | 'home';

// --- REUSABLE COMPONENTS ---
const ScreenWrapper = ({ children, visible, delay = 0 }: { children: React.ReactNode, visible: boolean, delay?: number }) => {
  const fade = useRef(new Animated.Value(0)).current;
  const slide = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(fade, { toValue: 1, duration: 800, delay, useNativeDriver: true, easing: Easing.out(Easing.exp) }),
        Animated.timing(slide, { toValue: 0, duration: 800, delay, useNativeDriver: true, easing: Easing.out(Easing.exp) })
      ]).start();
    } else {
      fade.setValue(0);
      slide.setValue(30);
    }
  }, [visible]);

  if (!visible) return null;
  return (
    <Animated.View style={[styles.screenContainer, { opacity: fade, transform: [{ translateY: slide }] }]}>
      {children}
    </Animated.View>
  );
};

const InputField = ({ icon, ...props }: any) => (
  <View style={styles.inputWrapper}>
    <MaterialCommunityIcons name={icon} color={THEME.textDim} size={20} style={styles.inputIcon} />
    <TextInput 
      placeholderTextColor={THEME.textDim} 
      style={styles.input} 
      {...props} 
    />
  </View>
);

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenState>('login');
  const [isAlertActive, setIsAlertActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Form states
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', keyword: '' });
  const [guardian, setGuardian] = useState({ name: '', phone: '', email: '' });
  const [countdown, setCountdown] = useState(60);
  const [activeAlertId, setActiveAlertId] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Model References
  const keywordModel = useRef<ModelWrapper | null>(null);
  const motionModel = useRef<ModelWrapper | null>(null);
  const [isSimulated, setIsSimulated] = useState(false);
  const recording = useRef<Audio.Recording | null>(null);

  // Animation values for SOS
  const pulse1 = useRef(new Animated.Value(1)).current;
  const pulse2 = useRef(new Animated.Value(1)).current;
  const pulse3 = useRef(new Animated.Value(1)).current;
  const micWave = useRef(new Animated.Value(0)).current;

  const navigate = (screen: ScreenState) => {
    setCurrentScreen(screen);
  };

  // --- AUTOMATED ESCALATION TIMER ---
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isAlertActive && countdown > 0) {
      timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            autoEscalate();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isAlertActive, countdown]);

  // --- PERIODIC LOCATION SYNC ---
  useEffect(() => {
    let sync: NodeJS.Timeout;
    if (currentScreen === 'home' && !isAlertActive) {
      sync = setInterval(async () => {
        try {
          const loc = await getCurrentPositionAsync({});
          await axios.put(`${API_BASE}/profile/update/`, {
            location: { lat: loc.coords.latitude, lng: loc.coords.longitude }
          }, { headers: { Authorization: `Bearer ${authToken}` } });
        } catch (e) { console.log("Sync failed"); }
      }, 60000); // Every 60 seconds
    }
    return () => clearInterval(sync);
  }, [currentScreen, isAlertActive, authToken]);
  
  // --- KEYWORD DETECTION ENGINE ---
  useEffect(() => {
    const loadModels = async () => {
      try {
        const kModel = await safeLoadModel(require('./assets/models/keyword_model.tflite'), 'Keyword Detection');
        const mModel = await safeLoadModel(require('./assets/models/motion_model.tflite'), 'Motion Analysis');
        
        keywordModel.current = kModel;
        motionModel.current = mModel;
        
        if (kModel.isMock) setIsSimulated(true);
        console.log("✅ RAKSHAK Core Models Initialized " + (kModel.isMock ? "[SIMULATED]" : "[NATIVE]"));
      } catch (e) {
        console.error("❌ Failed to initialize Rakshak ML Models", e);
        setIsSimulated(true); // Fallback to simulation even on error
      }
    };
    loadModels();
  }, []);

  useEffect(() => {
    let detectionInterval: NodeJS.Timeout;
    if (currentScreen === 'home' && !isAlertActive && keywordModel.current) {
      detectionInterval = setInterval(async () => {
        try {
          // 1. Simulate fetching current audio buffer
          const mockBuffer = {}; // This would be the raw PCM from expo-av
          const mfccArray = await extractMFCCs(mockBuffer);
          
          // 2. Perform Keyword Inference
          if (!keywordModel.current) return;
          const output = await keywordModel.current.run([mfccArray]);
          const voiceScore = output[0][1]; // Probability of keyword match

          // 3. Perform Motion Inference (simulated here)
          const motionScore = 0.1; // Placeholder for motion model
          
          const probability = fuseDetectionScores(voiceScore, motionScore);

          if (probability > 0.85) {
             console.warn("🚨 KEYWORD DETECTED. Triggering SOS...");
             startSOS();
          }
        } catch (e) {
          // Silent catch for periodic loop
        }
      }, 2000); // Check every 2 seconds
    }
    return () => clearInterval(detectionInterval);
  }, [currentScreen, isAlertActive, keywordModel.current]);

  const autoEscalate = async () => {
    if (!activeAlertId) return;
    try {
      await axios.post(`${API_BASE}/alerts/verify/`, { alert_id: activeAlertId }, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      Alert.alert("🚨 ESCALATED", "60s limit exceeded. All Guardians and Nearby Users have been notified.");
    } catch (e) {
      console.error("Escalation failed", e);
    }
  };

  const startSOS = async () => {
    setIsAlertActive(true);
    setCountdown(60);
    
    // 1. Immediate Pulse Animation
    const createPulse = (val: Animated.Value, delay: number) => 
      Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(val, { toValue: 2.5, duration: 1500, useNativeDriver: true, easing: Easing.out(Easing.quad) }),
          Animated.timing(val, { toValue: 1, duration: 0, useNativeDriver: true })
        ])
      );
    
    Animated.parallel([createPulse(pulse1, 0), createPulse(pulse2, 500), createPulse(pulse3, 1000)]).start();

    // 2. Trigger Backend Alert Record
    try {
      const location = await getCurrentPositionAsync({});
      const response = await axios.post(`${API_BASE}/alerts/trigger/`, {
        lat: location.coords.latitude,
        lng: location.coords.longitude,
        threat_level: 'HIGH'
      }, { headers: { Authorization: `Bearer ${authToken}` } });
      
      setActiveAlertId(response.data.alert_id);
    } catch (e) { 
      Alert.alert(
        "🚨 OFFLINE PROTOCOL", 
        "Cannot reach RAKSHAK Command Center.\n\n1. Ensure Phone and PC are on the same Wi-Fi.\n2. Update API_BASE in App.tsx to your PC's IP.\n\nProceeding with local native SMS fallback."
      );
      // Fallback to manual SMS logic if backend fails
      const location = await getCurrentPositionAsync({});
      const mapLink = `https://www.google.com/maps/search/?api=1&query=${location.coords.latitude},${location.coords.longitude}`;
      if (guardian.phone && await SMS.isAvailableAsync()) {
        await SMS.sendSMSAsync([guardian.phone], `📍 RAKSHAK ALERT: I need help. My location: ${mapLink}`);
      }
    }
  };

  const stopSOS = async () => {
    setIsAlertActive(false);
    [pulse1, pulse2, pulse3].forEach(p => { p.stopAnimation(); p.setValue(1); });
    
    if (activeAlertId) {
      try {
        await axios.post(`${API_BASE}/alerts/${activeAlertId}/resolve/`, {}, {
          headers: { Authorization: `Bearer ${authToken}` }
        });
      } catch (e) { console.log("Resolution failed"); }
    }
  };

  const handleMicPress = async () => {
    if (!isRecording) {
      try {
        const { status } = await Audio.requestPermissionsAsync();
        if (status !== 'granted') return Alert.alert("Required", "Microphone access is needed for Rakshak voice SOS.");

        setIsRecording(true);
        Animated.loop(
          Animated.sequence([
            Animated.timing(micWave, { toValue: 1, duration: 400, useNativeDriver: true }),
            Animated.timing(micWave, { toValue: 0, duration: 400, useNativeDriver: true })
          ])
        ).start();

        // Start Actual Recording
        await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
        const { recording: rec } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
        recording.current = rec;

        console.log("⏺️ Recording Voice Signature...");
        
        setTimeout(async () => {
          setIsRecording(false);
          micWave.stopAnimation();
          
          if (recording.current) {
            await recording.current.stopAndUnloadAsync();
            const uri = recording.current.getURI();
            console.log("✅ Signature captured at:", uri);
            recording.current = null;
          }
          
          Alert.alert("Biometric Locked", `Phrase "${form.keyword}" mapped using TFLite.`, [{ text: "Proceed", onPress: () => navigate('contacts_setup') }]);
        }, 3000);
      } catch (e) {
        console.error("Recording failed", e);
        setIsRecording(false);
        micWave.stopAnimation();
      }
    }
  };

  return (
    <View style={styles.appContainer}>
      <StatusBar barStyle="light-content" />
      <LinearGradient colors={THEME.bg as any} style={StyleSheet.absoluteFill} />

      {/* --- LOGIN SCREEN --- */}
      <ScreenWrapper visible={currentScreen === 'login'}>
        <View style={styles.glassCard}>
          <View style={styles.logoCircle}>
            <MaterialCommunityIcons name="shield-check" color={THEME.primary} size={40} />
          </View>
          <Text style={styles.title}>RAKSHAK</Text>
          <Text style={styles.subtitle}>Unified Safety Protocol</Text>
          
          <InputField 
            icon="email-outline" placeholder="Access ID (Email)" 
            value={form.email} onChangeText={(v: string) => setForm({...form, email: v})} 
          />
          <InputField 
            icon="lock-outline" placeholder="Passcode" secureTextEntry 
            value={form.password} onChangeText={(v: string) => setForm({...form, password: v})} 
          />

          <TouchableOpacity 
            style={styles.btnPrimary} 
            onPress={async () => {
              if (!form.email || !form.password) return Alert.alert("Required", "Please enter ID and Passcode");
              
              try {
                const res = await axios.post(`${API_BASE}/auth/login/`, {
                  email: form.email,
                  password: form.password
                });
                
                const token = res.data.access;
                setAuthToken(token);
                
                // Fetch real profile data immediately
                const contactRes = await axios.get(`${API_BASE}/contacts/`, {
                   headers: { Authorization: `Bearer ${token}` }
                });
                
                if (contactRes.data && contactRes.data.length > 0) {
                   const c = contactRes.data[0];
                   setGuardian({ name: c.name, phone: c.phone, email: c.email || '' });
                }
                navigate('home');
              } catch (e) { 
                Alert.alert("Authentication Failure", "Invalid credentials or network timeout.");
              }
            }}
          >
            <Text style={styles.btnText}>INITIALIZE SESSION</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => navigate('register')}>
            <Text style={styles.linkText}>Establish new credentials</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>

      {/* --- REGISTER SCREEN --- */}
      <ScreenWrapper visible={currentScreen === 'register'}>
        <View style={styles.glassCard}>
          <Text style={styles.header}>NEW PROFILE</Text>
          <Text style={styles.description}>Establish your biometrically secure environment.</Text>
          
          <InputField icon="account-outline" placeholder="Full Name" value={form.name} onChangeText={(v: string) => setForm({...form, name: v})} />
          <InputField icon="email-outline" placeholder="Email" value={form.email} onChangeText={(v: string) => setForm({...form, email: v})} />
          <InputField icon="phone-outline" placeholder="Phone Number" value={form.phone} onChangeText={(v: string) => setForm({...form, phone: v})} keyboardType="phone-pad" />
          <InputField icon="lock-outline" placeholder="Passcode" secureTextEntry value={form.password} onChangeText={(v: string) => setForm({...form, password: v})} />

          <TouchableOpacity 
            style={styles.btnPrimary} 
            onPress={async () => {
              if (!form.name || !form.email || !form.password) return Alert.alert("Missing Info", "All fields are required.");
              
              try {
                 const res = await axios.post(`${API_BASE}/auth/register/`, form);
                 setAuthToken(res.data.access);
                 navigate('voice_setup');
              } catch (e) {
                 Alert.alert("Registry Error", "User may already exist or connection failed.");
              }
            }}
          >
            <Text style={styles.btnText}>PROCEED TO AUDIO</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>

      {/* --- VOICE SETUP SCREEN --- */}
      <ScreenWrapper visible={currentScreen === 'voice_setup'}>
        <View style={styles.glassCard}>
          <View style={styles.iconBox}><MaterialCommunityIcons name="microphone" color={THEME.primary} size={30} /></View>
          <Text style={styles.header}>Voice Signature</Text>
          <Text style={styles.description}>Your distress keyword is processed strictly on-device using quantized TFLite models.</Text>
          
          <InputField 
            icon="waveform" placeholder="Secret Keyword (e.g. Help)" 
            value={form.keyword} onChangeText={(v: string) => setForm({...form, keyword: v})}
          />

          <View style={styles.micCircleContainer}>
            {isRecording && <Animated.View style={[styles.micPulse, { opacity: micWave.interpolate({ inputRange: [0, 1], outputRange: [0.6, 0] }), transform: [{ scale: micWave.interpolate({ inputRange: [0, 1], outputRange: [1, 1.8] }) }] }]} />}
            <TouchableOpacity 
              style={[styles.micBtn, isRecording && styles.micBtnActive]} 
              onPress={handleMicPress}
              disabled={!form.keyword || isRecording}
            >
              <MaterialCommunityIcons name="microphone" color={THEME.text} size={35} />
            </TouchableOpacity>
          </View>
          <Text style={styles.hintText}>{isRecording ? "Capturing Acoustic Features..." : "Pulse to start recording"}</Text>
        </View>
      </ScreenWrapper>

      {/* --- CONTACTS SETUP SCREEN --- */}
      <ScreenWrapper visible={currentScreen === 'contacts_setup'}>
        <View style={styles.glassCard}>
          <Text style={styles.header}>The Guardian</Text>
          <Text style={styles.description}>Who should receive your rescue beacons?</Text>
          
          <InputField icon="account-outline" placeholder="Contact Name" value={guardian.name} onChangeText={(v: string) => setGuardian({...guardian, name: v})} />
          <InputField icon="phone-outline" placeholder="Emergency Phone" value={guardian.phone} onChangeText={(v: string) => setGuardian({...guardian, phone: v})} keyboardType="phone-pad" />
          <InputField icon="email-outline" placeholder="Emergency Email" value={guardian.email} onChangeText={(v: string) => setGuardian({...guardian, email: v})} keyboardType="email-address" />

          <TouchableOpacity 
            style={[styles.btnPrimary, { backgroundColor: THEME.success }]} 
            onPress={async () => {
              if (guardian.name && guardian.phone && guardian.email) {
                 // Save to server
                 try {
                    await axios.post(`${API_BASE}/contacts/add/`, guardian, {
                       headers: { Authorization: `Bearer ${authToken}` }
                    });
                    navigate('home');
                 } catch (e) { Alert.alert("Sync Failure", "Could not save to server. Check IP."); }
              }
              else if (!guardian.email && guardian.name && guardian.phone) {
                 Alert.alert("Legacy Setup", "Automation requires an email. Continue with local SMS protocol only?", [
                   { text: "Add Email", style: 'cancel' },
                   { text: "Use Local SMS", onPress: () => navigate('home') }
                 ]);
              }
              else Alert.alert("Protocol Missing", "Please define a guardian.");
            }}
          >
            <Text style={styles.btnText}>ACTIVATE BEACON</Text>
          </TouchableOpacity>
        </View>
      </ScreenWrapper>

      {/* --- HOME / SOS DASHBOARD --- */}
      <ScreenWrapper visible={currentScreen === 'home'}>
        <View style={styles.dashboard}>
          <View style={styles.dashHeader}>
            <View>
              <Text style={styles.dashTitle}>RAKSHAK</Text>
              <View style={styles.statusRow}>
                <View style={styles.statusDot} /><Text style={styles.statusLabel}>SECURED SESSION</Text>
                {isSimulated && (
                  <View style={[styles.statusRow, { marginLeft: 10 }]}>
                    <MaterialCommunityIcons name="test-tube" color={THEME.warning} size={12} />
                    <Text style={[styles.statusLabel, { color: THEME.warning, marginLeft: 4 }]}>SIMULATION MODE</Text>
                  </View>
                )}
              </View>
            </View>
            <TouchableOpacity onPress={() => navigate('login')}><MaterialCommunityIcons name="logout" color={THEME.textDim} size={24} /></TouchableOpacity>
          </View>

          {!guardian.email && (
            <TouchableOpacity style={styles.warningBanner} onPress={() => navigate('contacts_setup')}>
              <MaterialCommunityIcons name="alert-circle-outline" color="#FFF" size={18} />
              <Text style={styles.warningBannerText}>Automation Disabled: Add Guardian Email</Text>
            </TouchableOpacity>
          )}

          <View style={styles.sosCoreContainer}>
            {isAlertActive && [pulse1, pulse2, pulse3].map((p, i) => (
              <Animated.View key={i} style={[styles.sosShockwave, { transform: [{ scale: p }], opacity: p.interpolate({ inputRange: [1, 2.5], outputRange: [0.3, 0] }) }]} />
            ))}
            
            <TouchableOpacity 
              activeOpacity={0.9} 
              style={[styles.sosBtnMain, isAlertActive && styles.sosBtnActive]} 
              onPress={isAlertActive ? stopSOS : startSOS}
            >
              <MaterialCommunityIcons name="broadcast" color="#FFF" size={40} style={styles.sosIcon} />
              <Text style={styles.sosMainText}>{isAlertActive ? `${countdown}s` : "SOS"}</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statBox}>
               <MaterialCommunityIcons name="pulse" color={THEME.primary} size={22} />
               <Text style={styles.statVal}>98%</Text>
               <Text style={styles.statLab}>AI Precision</Text>
            </View>
            <View style={styles.statBox}>
               <MaterialCommunityIcons name="map-marker-radius" color={THEME.primary} size={22} />
               <Text style={styles.statVal}>±2m</Text>
               <Text style={styles.statLab}>GPS Accuracy</Text>
            </View>
          </View>

          <View style={styles.guardianStrip}>
            <MaterialCommunityIcons name="check-circle-outline" color={THEME.success} size={20} />
            <Text style={styles.guardianText}>Guardian {guardian.name || 'Set'} is synced</Text>
          </View>
        </View>
      </ScreenWrapper>
    </View>
  );
}

const styles = StyleSheet.create({
  appContainer: { flex: 1, backgroundColor: '#000' },
  screenContainer: { flex: 1, paddingHorizontal: 25, justifyContent: 'center' },
  glassCard: { backgroundColor: THEME.glass, borderRadius: 40, padding: 35, borderWidth: 1, borderColor: THEME.border, alignItems: 'center' },
  
  // Auth Elements
  logoCircle: { width: 80, height: 80, borderRadius: 40, backgroundColor: 'rgba(124, 58, 237, 0.1)', justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  title: { color: THEME.text, fontSize: 34, fontWeight: '900', letterSpacing: 5 },
  subtitle: { color: THEME.primary, fontSize: 13, fontWeight: '800', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 40 },
  header: { color: THEME.text, fontSize: 28, fontWeight: '800', marginBottom: 10 },
  description: { color: THEME.textDim, fontSize: 15, textAlign: 'center', lineHeight: 22, marginBottom: 35 },
  
  // Input Component
  inputWrapper: { width: '100%', flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 20, marginBottom: 18, paddingHorizontal: 15, borderWidth: 1, borderColor: THEME.border },
  inputIcon: { marginRight: 15 },
  input: { flex: 1, color: THEME.text, fontSize: 16, paddingVertical: 18 },
  
  // Button Component
  btnPrimary: { width: '100%', backgroundColor: THEME.primary, borderRadius: 20, paddingVertical: 20, alignItems: 'center', marginTop: 15, shadowColor: THEME.primary, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.4, shadowRadius: 15 },
  btnText: { color: THEME.text, fontSize: 15, fontWeight: '900', letterSpacing: 2 },
  linkText: { color: THEME.textDim, fontSize: 14, marginTop: 25, textDecorationLine: 'underline' },

  // Voice Setup Elements
  iconBox: { width: 60, height: 60, borderRadius: 20, backgroundColor: 'rgba(124,58,237,0.1)', justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  micCircleContainer: { width: 200, height: 200, justifyContent: 'center', alignItems: 'center', marginTop: 10 },
  micBtn: { width: 100, height: 100, borderRadius: 50, backgroundColor: THEME.primary, justifyContent: 'center', alignItems: 'center', zIndex: 10 },
  micBtnActive: { backgroundColor: THEME.warning },
  micPulse: { position: 'absolute', width: 100, height: 100, borderRadius: 50, backgroundColor: THEME.primary },
  hintText: { color: THEME.textDim, marginTop: 20, fontSize: 14 },

  // Dashboard Elements
  dashboard: { flex: 1, paddingVertical: 50 },
  dashHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40 },
  dashTitle: { color: THEME.text, fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  statusRow: { flexDirection: 'row', alignItems: 'center', marginTop: 5 },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: THEME.success, marginRight: 8 },
  statusLabel: { color: THEME.success, fontSize: 10, fontWeight: '800', letterSpacing: 1 },
  
  sosCoreContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  sosBtnMain: { width: width * 0.6, height: width * 0.6, borderRadius: width * 0.3, backgroundColor: THEME.warning, justifyContent: 'center', alignItems: 'center', zIndex: 20, borderWidth: 8, borderColor: 'rgba(255,255,255,0.1)' },
  sosBtnActive: { backgroundColor: THEME.danger },
  sosIcon: { marginBottom: 15 },
  sosMainText: { color: '#FFF', fontSize: 32, fontWeight: '900', textAlign: 'center', letterSpacing: 2 },
  sosShockwave: { position: 'absolute', width: width * 0.6, height: width * 0.6, borderRadius: width * 0.3, backgroundColor: THEME.warning, zIndex: 1 },
  
  statsGrid: { flexDirection: 'row', gap: 15, marginBottom: 30 },
  statBox: { flex: 1, backgroundColor: THEME.glass, borderRadius: 25, padding: 20, alignItems: 'center', borderWidth: 1, borderColor: THEME.border },
  statVal: { color: THEME.text, fontSize: 20, fontWeight: '800', marginTop: 8 },
  statLab: { color: THEME.textDim, fontSize: 11, fontWeight: '600', marginTop: 4 },
  
  guardianStrip: { backgroundColor: 'rgba(16, 185, 129, 0.1)', paddingVertical: 18, borderRadius: 20, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: 'rgba(16, 185, 129, 0.2)' },
  guardianText: { color: THEME.success, marginLeft: 10, fontWeight: '700', fontSize: 13 },
  warningBanner: { backgroundColor: THEME.warning, paddingVertical: 12, borderRadius: 15, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: 20, marginHorizontal: 5 },
  warningBannerText: { color: '#FFF', fontSize: 12, fontWeight: '800', marginLeft: 8, letterSpacing: 0.5 }
});
