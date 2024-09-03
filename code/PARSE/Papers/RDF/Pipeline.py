import subprocess

def run_script(filename):
    subprocess.check_call(['C:\\Users\\bowen\\anaconda3\\python.exe', filename])

if __name__ == '__main__':
    run_script('C:\\Users\\bowen\PycharmProjects\\anu-scholarly-kg\src\Papers\\utils\paper2BIO.py.py')
    run_script('C:\\Users\bowen\PycharmProjects\anu-scholarly-kg\src\Papers\Models\models\ner_model_v9\predict.py')
    run_script('C:\\Users\bowen\PycharmProjects\anu-scholarly-kg\src\Papers\Models\models\nel_models\wikidata_v1.py')
    run_script(
        'C:\\Users\bowen\PycharmProjects\anu-scholarly-kg\src\Papers\Models\models\keyword_model\keyword_model.py')
    run_script(
        'C:\\Users\bowen\PycharmProjects\anu-scholarly-kg\src\Papers\Models\models\summarization_model\summarize.py')
    run_script('C:\\Users\bowen\PycharmProjects\anu-scholarly-kg\src\Papers\RDF\RDF_Constrcut.py')
