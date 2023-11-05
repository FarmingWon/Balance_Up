def mongo_key():
    with open('C:/Users/DSL/Desktop/Balance_Up/api_key/mongo.txt', 'r', encoding='utf-8') as file:
        return file.read()
    
def finetuned_gpt_key():
    with open('api_key/finetuned_gpt.txt', 'r', encoding='utf-8') as file:
        return file.read()

def gpt_key():
    with open('api_key/gpt_key.txt', 'r', encoding='utf-8') as file:
        
        return file.read()
def get_path(two_path):
    path = f"C:/Users/DSL/Desktop/Balance_Up/{two_path}"
    return path

if __name__ == "__main__":
    print(mongo_key())