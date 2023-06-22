import onnxruntime

all_faces = None
providers = onnxruntime.get_available_providers()
args = None

if 'TensorrtExecutionProvider' in providers:
    providers.remove('TensorrtExecutionProvider')
