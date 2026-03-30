# Expo ML Integration Guide

To successfully run our quantized TensorFlow Lite models natively on the Expo mobile app:

## 1. Install Library
```bash
npm install react-native-fast-tflite
```

## 2. Locate Models
You must ship these models with the build. Download the provided `.tflite` files from the ML team and place them inside the mobile source tree:
- \`mobile/assets/models/keyword_model.tflite\`
- \`mobile/assets/models/motion_model.tflite\`

## 3. Load the Models
```typescript
import { loadTensorflowModel } from 'react-native-fast-tflite';

const keywordModel = await loadTensorflowModel(require('../assets/models/keyword_model.tflite'));
const motionModel  = await loadTensorflowModel(require('../assets/models/motion_model.tflite'));
```

## 4. Run Inference Loop (Inside Background Task)
Every 2 seconds, evaluate both models.

**For Motion (100 * 6 readings normalized from [-1, 1]):**
```typescript
const output = await motionModel.run([sensorArray]);
const motion_score = output[0][2]; // Probability of severe risk
```

**For Audio (40 MFCC array extraction algorithm applied to buffer):**
```typescript
const output = await keywordModel.run([mfccArray]);
const voice_score = output[0][1]; // Probability of keyword match
```

## 5. Fuse & Trigger API
Combine via the established heuristic weights: `(voice * 0.6) + (motion * 0.4)`.

If \`HIGH\` -> trigger the backend POST \`/api/alerts/trigger/\`.
