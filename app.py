from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Load the trained model
with open('model/crop_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load feature names
with open('model/feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

# Crop name translations - Actual agricultural names in Indian languages
crop_names_multilingual = {
    'rice': {
        'en': 'Rice', 'hi': 'धान', 'te': 'వరి', 'ta': 'அரிசி', 'ml': 'നെല്ല്',
        'kn': 'ಅಕ್ಕಿ', 'mr': 'तांदूळ', 'bn': 'ধান', 'gu': 'ચોખા', 'pa': 'ਚੌਲ'
    },
    'maize': {
        'en': 'Maize', 'hi': 'मक्का', 'te': 'మొక్కజొన్న', 'ta': 'சோளம்', 'ml': 'ചോളം',
        'kn': 'ಮೆಕ್ಕೆ ಜೋಳ', 'mr': 'मका', 'bn': 'ভুট্টা', 'gu': 'મકાઈ', 'pa': 'ਮੱਕੀ'
    },
    'chickpea': {
        'en': 'Chickpea', 'hi': 'चना', 'te': 'శనగలు', 'ta': 'கொண்டைக்கடலை', 'ml': 'കടല',
        'kn': 'ಕಡಲೆ', 'mr': 'हरभरा', 'bn': 'ছোলা', 'gu': 'ચણા', 'pa': 'ਛੋਲੇ'
    },
    'kidneybeans': {
        'en': 'Kidney Beans', 'hi': 'राजमा', 'te': 'రాజ్మా', 'ta': 'ராஜ்மா', 'ml': 'രാജ്മ',
        'kn': 'ರಾಜ್ಮಾ', 'mr': 'राजमा', 'bn': 'রাজমা', 'gu': 'રાજમા', 'pa': 'ਰਾਜਮਾਂ'
    },
    'pigeonpeas': {
        'en': 'Pigeon Peas', 'hi': 'अरहर', 'te': 'కందులు', 'ta': 'துவரை', 'ml': 'തുവര',
        'kn': 'ತೊಗರಿ ಬೇಳೆ', 'mr': 'तूर', 'bn': 'অড়হর', 'gu': 'અરહર', 'pa': 'ਅਰਹਰ'
    },
    'mothbeans': {
        'en': 'Moth Beans', 'hi': 'मोठ', 'te': 'మినుములు', 'ta': 'மொச்சை', 'ml': 'മോത്ത്',
        'kn': 'ಹೆಸರುಕಾಳು', 'mr': 'मटकी', 'bn': 'মথ', 'gu': 'મઠ', 'pa': 'ਮੋਠ'
    },
    'mungbean': {
        'en': 'Mung Bean', 'hi': 'मूंग', 'te': 'పెసలు', 'ta': 'பயறு', 'ml': 'ചെറുപയർ',
        'kn': 'ಹೆಸರು', 'mr': 'मूग', 'bn': 'মুগ', 'gu': 'મગ', 'pa': 'ਮੂੰਗ'
    },
    'blackgram': {
        'en': 'Black Gram', 'hi': 'उड़द', 'te': 'మినుములు', 'ta': 'உளுந்து', 'ml': 'ഉഴുന്ന്',
        'kn': 'ಉದ್ದು', 'mr': 'उडीद', 'bn': 'মাষকলাই', 'gu': 'અડદ', 'pa': 'ਮਾਂਹ'
    },
    'lentil': {
        'en': 'Lentil', 'hi': 'मसूर', 'te': 'మసూర్', 'ta': 'மசூர்', 'ml': 'മസൂർ',
        'kn': 'ಮಸೂರ', 'mr': 'मसूर', 'bn': 'মসুর', 'gu': 'મસૂર', 'pa': 'ਮਸੂਰ'
    },
    'pomegranate': {
        'en': 'Pomegranate', 'hi': 'अनार', 'te': 'దానిమ్మ', 'ta': 'மாதுளை', 'ml': 'മാതളനാരകം',
        'kn': 'ದಾಳಿಂಬೆ', 'mr': 'डाळिंब', 'bn': 'ডালিম', 'gu': 'દાડમ', 'pa': 'ਅਨਾਰ'
    },
    'banana': {
        'en': 'Banana', 'hi': 'केला', 'te': 'అరటి', 'ta': 'வாழை', 'ml': 'വാഴപ്പഴം',
        'kn': 'ಬಾಳೆ', 'mr': 'केळी', 'bn': 'কলা', 'gu': 'કેળા', 'pa': 'ਕੇਲਾ'
    },
    'mango': {
        'en': 'Mango', 'hi': 'आम', 'te': 'మామిడి', 'ta': 'மாம்பழம்', 'ml': 'മാങ്ങ',
        'kn': 'ಮಾವಿನ ಹಣ್ಣು', 'mr': 'आंबा', 'bn': 'আম', 'gu': 'કેરી', 'pa': 'ਅੰਬ'
    },
    'grapes': {
        'en': 'Grapes', 'hi': 'अंगूर', 'te': 'ద్రాక్ష', 'ta': 'திராட்சை', 'ml': 'മുന്തിരി',
        'kn': 'ದ್ರಾಕ್ಷಿ', 'mr': 'द्राक्षे', 'bn': 'আঙ্গুর', 'gu': 'દ્રાક્ષ', 'pa': 'ਅੰਗੂਰ'
    },
    'watermelon': {
        'en': 'Watermelon', 'hi': 'तरबूज', 'te': 'పుచ్చకాయ', 'ta': 'தர்பூசணி', 'ml': 'തണ്ണിമത്തൻ',
        'kn': 'ಕಲ್ಲಂಗಡಿ', 'mr': 'टरबूज', 'bn': 'তরমুজ', 'gu': 'તરબૂચ', 'pa': 'ਤਰਬੂਜ'
    },
    'muskmelon': {
        'en': 'Muskmelon', 'hi': 'खरबूजा', 'te': 'ఖర్బూజా', 'ta': 'முலாம்பழம்', 'ml': 'മധുരപ്പഴം',
        'kn': 'ಖರ್ಬೂಜ', 'mr': 'खरबूज', 'bn': 'ফুটি', 'gu': 'ખરબૂચ', 'pa': 'ਖਰਬੂਜਾ'
    },
    'apple': {
        'en': 'Apple', 'hi': 'सेब', 'te': 'ఆపిల్', 'ta': 'ஆப்பிள்', 'ml': 'ആപ്പിൾ',
        'kn': 'ಸೇಬು', 'mr': 'सफरचंद', 'bn': 'আপেল', 'gu': 'સફરજન', 'pa': 'ਸੇਬ'
    },
    'orange': {
        'en': 'Orange', 'hi': 'संतरा', 'te': 'నారింజ', 'ta': 'ஆரஞ்சு', 'ml': 'ഓറഞ്ച്',
        'kn': 'ಕಿತ್ತಳೆ', 'mr': 'संत्रा', 'bn': 'কমলা', 'gu': 'નારંગી', 'pa': 'ਸੰਤਰਾ'
    },
    'papaya': {
        'en': 'Papaya', 'hi': 'पपीता', 'te': 'బొప్పాయి', 'ta': 'பப்பாளி', 'ml': 'പപ്പായ',
        'kn': 'ಪಪ್ಪಾಯಿ', 'mr': 'पपई', 'bn': 'পেঁপে', 'gu': 'પપૈયા', 'pa': 'ਪਪੀਤਾ'
    },
    'coconut': {
        'en': 'Coconut', 'hi': 'नारियल', 'te': 'కొబ్బరి', 'ta': 'தேங்காய்', 'ml': 'തേങ്ങ',
        'kn': 'ತೆಂಗು', 'mr': 'नारळ', 'bn': 'নারকেল', 'gu': 'નાળિયેર', 'pa': 'ਨਾਰੀਅਲ'
    },
    'cotton': {
        'en': 'Cotton', 'hi': 'कपास', 'te': 'పత్తి', 'ta': 'பருத்தி', 'ml': 'പഞ്ഞി',
        'kn': 'ಹತ್ತಿ', 'mr': 'कापूस', 'bn': 'তুলা', 'gu': 'કપાસ', 'pa': 'ਕਪਾਹ'
    },
    'jute': {
        'en': 'Jute', 'hi': 'जूट', 'te': 'జనపనార', 'ta': 'சணல்', 'ml': 'ചണം',
        'kn': 'ಸೆಣಬು', 'mr': 'तांबूस', 'bn': 'পাট', 'gu': 'શણ', 'pa': 'ਜੂਟ'
    },
    'coffee': {
        'en': 'Coffee', 'hi': 'कॉफी', 'te': 'కాఫీ', 'ta': 'காபி', 'ml': 'കാപ്പി',
        'kn': 'ಕಾಫಿ', 'mr': 'कॉफी', 'bn': 'কফি', 'gu': 'કોફી', 'pa': 'ਕੌਫੀ'
    }
}

# Crop information with recommendations
crop_info = {
    'rice': {
        'name': 'Rice',
        'description': 'Rice is a staple food crop that requires high water and humidity. Best grown in flooded fields.',
        'season': 'Kharif (June-November)',
        'soil_type': 'Clay or loamy soil',
        'tips': 'Ensure proper water management, use quality seeds, and monitor for pests regularly.'
    },
    'maize': {
        'name': 'Maize (Corn)',
        'description': 'Maize is a cereal grain that thrives in warm conditions with moderate rainfall.',
        'season': 'Kharif and Rabi',
        'soil_type': 'Well-drained loamy soil',
        'tips': 'Maintain proper spacing, apply nitrogen-rich fertilizers, and protect from birds.'
    },
    'chickpea': {
        'name': 'Chickpea',
        'description': 'Chickpea is a protein-rich legume crop suitable for dry regions.',
        'season': 'Rabi (October-March)',
        'soil_type': 'Well-drained loamy soil',
        'tips': 'Avoid waterlogging, use proper seed treatment, and rotate crops for better yield.'
    },
    'kidneybeans': {
        'name': 'Kidney Beans',
        'description': 'Kidney beans are nutritious legumes that prefer warm climates.',
        'season': 'Kharif',
        'soil_type': 'Well-drained fertile soil',
        'tips': 'Provide support for climbing varieties and ensure adequate nitrogen.'
    },
    'pigeonpeas': {
        'name': 'Pigeon Peas',
        'description': 'Pigeon peas are drought-resistant legumes suitable for semi-arid regions.',
        'season': 'Kharif',
        'soil_type': 'Various soil types',
        'tips': 'Requires less water, good for intercropping, and fixes nitrogen in soil.'
    },
    'mothbeans': {
        'name': 'Moth Beans',
        'description': 'Moth beans are drought-resistant and suitable for arid regions.',
        'season': 'Kharif',
        'soil_type': 'Sandy loam',
        'tips': 'Very drought tolerant, requires minimal water and fertilizer.'
    },
    'mungbean': {
        'name': 'Mung Bean',
        'description': 'Mung beans are fast-growing legumes rich in protein.',
        'season': 'Kharif and Summer',
        'soil_type': 'Loamy soil',
        'tips': 'Short duration crop, good for rotation, and improves soil fertility.'
    },
    'blackgram': {
        'name': 'Black Gram',
        'description': 'Black gram is a pulse crop suitable for various climatic conditions.',
        'season': 'Kharif and Rabi',
        'soil_type': 'Loamy soil',
        'tips': 'Use certified seeds, maintain proper drainage, and control pests.'
    },
    'lentil': {
        'name': 'Lentil',
        'description': 'Lentils are cool-season legumes rich in protein.',
        'season': 'Rabi',
        'soil_type': 'Well-drained loamy soil',
        'tips': 'Avoid waterlogging, use recommended varieties, and harvest at proper maturity.'
    },
    'pomegranate': {
        'name': 'Pomegranate',
        'description': 'Pomegranate is a fruit crop suitable for semi-arid regions.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained soil',
        'tips': 'Requires pruning, proper irrigation, and protection from fruit cracking.'
    },
    'banana': {
        'name': 'Banana',
        'description': 'Banana is a tropical fruit requiring high moisture and warmth.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Rich loamy soil',
        'tips': 'Ensure regular watering, mulching, and protection from strong winds.'
    },
    'mango': {
        'name': 'Mango',
        'description': 'Mango is the king of fruits, requiring tropical to subtropical climate.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained deep soil',
        'tips': 'Prune regularly, manage flowering, and control pests and diseases.'
    },
    'grapes': {
        'name': 'Grapes',
        'description': 'Grapes are vine fruits suitable for warm and dry climates.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained sandy loam',
        'tips': 'Requires trellising, regular pruning, and disease management.'
    },
    'watermelon': {
        'name': 'Watermelon',
        'description': 'Watermelon is a summer fruit requiring warm weather and good moisture.',
        'season': 'Summer',
        'soil_type': 'Sandy loam',
        'tips': 'Provide adequate spacing, mulch well, and ensure consistent watering.'
    },
    'muskmelon': {
        'name': 'Muskmelon',
        'description': 'Muskmelon is a sweet summer fruit requiring warm conditions.',
        'season': 'Summer',
        'soil_type': 'Sandy loam',
        'tips': 'Maintain proper vine spacing, mulching, and protect from fruit flies.'
    },
    'apple': {
        'name': 'Apple',
        'description': 'Apples require temperate climate with cold winters.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained loamy soil',
        'tips': 'Requires chilling hours, proper pruning, and pest management.'
    },
    'orange': {
        'name': 'Orange',
        'description': 'Oranges are citrus fruits requiring warm subtropical climate.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained loamy soil',
        'tips': 'Regular watering, fertilization, and disease control are essential.'
    },
    'papaya': {
        'name': 'Papaya',
        'description': 'Papaya is a tropical fruit requiring warmth and good drainage.',
        'season': 'Year-round',
        'soil_type': 'Well-drained rich soil',
        'tips': 'Ensure good drainage, regular feeding, and remove male plants.'
    },
    'coconut': {
        'name': 'Coconut',
        'description': 'Coconut palms thrive in coastal tropical regions.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Sandy coastal soil',
        'tips': 'Requires regular watering in dry seasons and proper nutrient management.'
    },
    'cotton': {
        'name': 'Cotton',
        'description': 'Cotton is a fiber crop requiring warm weather and moderate rainfall.',
        'season': 'Kharif',
        'soil_type': 'Black cotton soil',
        'tips': 'Control bollworms, ensure proper spacing, and timely harvesting.'
    },
    'jute': {
        'name': 'Jute',
        'description': 'Jute is a fiber crop requiring high humidity and rainfall.',
        'season': 'Kharif',
        'soil_type': 'Alluvial soil',
        'tips': 'Requires waterlogged conditions, harvest at proper stage for quality fiber.'
    },
    'coffee': {
        'name': 'Coffee',
        'description': 'Coffee requires tropical highland climate with good rainfall.',
        'season': 'Year-round (perennial)',
        'soil_type': 'Well-drained rich soil',
        'tips': 'Provide shade, maintain proper moisture, and control pests and diseases.'
    }
}

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'mr': 'Marathi',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'pa': 'Punjabi'
}

def translate_text(text, target_lang='en', source_lang='auto'):
    """Translate text to target language"""
    if target_lang == 'en' or not text:
        return text
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Extract features
        N = float(data['nitrogen'])
        P = float(data['phosphorus'])
        K = float(data['potassium'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])
        
        # Get target language (default to English)
        target_lang = data.get('language', 'en')
        
        # Create feature array
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Get crop information
        info = crop_info.get(prediction, {
            'name': prediction.capitalize(),
            'description': 'Information not available',
            'season': 'N/A',
            'soil_type': 'N/A',
            'tips': 'N/A'
        })
        
        # Translate if needed
        if target_lang != 'en':
            # Use proper crop name from dictionary instead of translating
            crop_name_translated = crop_names_multilingual.get(prediction, {}).get(target_lang, info['name'])
            
            info = {
                'name': crop_name_translated,  # Use actual crop name, not translated
                'description': translate_text(info['description'], target_lang),
                'season': translate_text(info['season'], target_lang),
                'soil_type': translate_text(info['soil_type'], target_lang),
                'tips': translate_text(info['tips'], target_lang)
            }
        
        return jsonify({
            'success': True,
            'crop': prediction,
            'info': info,
            'language': target_lang
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/translate', methods=['POST'])
def translate():
    """Endpoint for translating UI text"""
    try:
        data = request.get_json()
        text = data['text']
        target_lang = data['target_lang']
        
        translated = translate_text(text, target_lang)
        
        return jsonify({
            'success': True,
            'translated': translated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/languages')
def get_languages():
    """Return supported languages"""
    return jsonify(SUPPORTED_LANGUAGES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
