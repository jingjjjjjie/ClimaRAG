import json

def load_corpus(filepath):
    with open(filepath, "r", encoding='utf-8') as file:
        raw_data = file.read()
    return json.loads(raw_data)

def display_results(result):
    print("---displaying the result---")
    if result['type'] == 'abstract':
        print('_____Querying Abstract Store_____')
        print('Here are the documents retrieved:')
        for doc in result['docs']:
            print(doc.metadata['title'], doc.metadata['year'])
        print(result['response'])
    
    elif result['type'] == 'content':
        print('_____Querying Content Store_____')
        print('Here are the documents retrieved:')
        print(result['docs'])
        print('\n')
        print('_____The response from LLM_____')
        print(result['response'])
    
    else:
        print(result['response']) 