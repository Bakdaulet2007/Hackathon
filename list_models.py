import google.generativeai as genai

# Вставь сюда свой ключ в кавычках
genai.configure(api_key="AIzaSyAhlYLJRhT7Cyh_ViBq5ppT89xN_9-fNgo")

# Получаем и печатаем все модели
models = genai.list_models()
for m in models:
    print(m.name)
