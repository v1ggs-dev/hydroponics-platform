import httpx
from datetime import datetime
from ai.config import IOT_BACKEND_URL

def fetch_sensor_data():
    """Fetch latest sensor data from the IoT platform backend."""
    try:
        response = httpx.get(f"{IOT_BACKEND_URL}/telemetry/latest", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                raw = data['data']
                # Transform their format to our standard format
                return {
                    'status': 'connected',
                    'temperature': raw.get('air_temperature', {}).get('value'),
                    'humidity': raw.get('humidity', {}).get('value'),
                    'tds': raw.get('tds', {}).get('value'),
                    'ph': raw.get('ph', {}).get('value'),
                    'moisture': raw.get('substrate_moisture', {}).get('value'),
                    'water_flow': raw.get('flow_rate', {}).get('value'),
                    'water_volume': raw.get('water_volume', {}).get('value'),
                    'timestamp': data.get('timestamp'),
                }
        return {'status': 'unavailable', 'message': 'IoT backend returned error'}
    except Exception as e:
        print(f"Could not fetch sensor data: {e}")
        return {'status': 'unavailable', 'message': str(e)}

def build_context(vision_result=None, sensor_data=None):
    """Build fusion context from AI-1 vision result + sensor data."""
    # If no sensor data passed, fetch it live
    if sensor_data is None:
        sensor_data = fetch_sensor_data()
    
    context = {
        'timestamp': datetime.now().isoformat(),
        'crop': None,
        'vision': None,
        'sensors': sensor_data,
    }
    
    if vision_result:
        predicted_class = vision_result.get('class', '')
        context['crop'] = predicted_class.split('___')[0] if '___' in predicted_class else None
        context['vision'] = {
            'class': predicted_class,
            'confidence': vision_result.get('confidence', 0)
        }
    
    return context
