from flask import Flask
from flask import request

import nltk

import soldier

app = Flask(__name__)


@app.route('/deploy')
def deploy():
    screen_name = "osdc_bot"
    screen_kill_comm = "screen -S {} -X quit".format(screen_name)
    screen_start_comm = 'screen -S "{}" -d -m'.format(screen_name)
    update_local_comm = "git pull origin master"
    start_bot_comm = 'screen -r "{0}" -X stuff "{1}"'.format(screen_name, "DEPLOY=1 nodejs chatbot.js\n")
    try:
        soldier.run(screen_kill_comm)
    except:
        pass

    print(soldier.run(update_local_comm).status_code)
    print(soldier.run(screen_start_comm).status_code)
    print(soldier.run(start_bot_comm).status_code)
    return 'Deployed'


@app.route('/howdoi')
def howdoi():
    command = soldier.run('howdoi {}'.format(request.args['query']))
    print(command.status_code)
    return '```\n{}\n```'.format(command.output)


@app.route('/general')
def general():
    command = request.args['query']
    words = nltk.word_tokenize(command)
    taggedTokens = nltk.pos_tag(words)
    outputCommand = ''
    for x in taggedTokens:
        if(x[0] == 'wiki' or x[0] == 'wikipedia'):
            outputCommand = outputCommand + 'wiki'
    regularExpression = r"""
                NP: {<NN|NNP|NNS>?<DT|PP\$>?<JJ>*<NN|NNS><IN>?<NN|NNP|NNS>+}
                {<VB>?<JJ>*<NNP|NN|NNS>+}
                """
    chunk = nltk.RegexpParser(regularExpression)
    sentenceTree = chunk.parse(taggedTokens)
    for outerSubtree in sentenceTree.subtrees():
        if outerSubtree.label() == 'NP':
            for innerSubtree in outerSubtree:
                if(innerSubtree[1] == 'NNP'):
                    outputCommand = outputCommand + ' ' + innerSubtree[0]
                elif(innerSubtree[1] == 'NN'):
                    if(innerSubtree[0] == 'location'):
                        outputCommand = outputCommand + ' ' + 'locate'
                    elif(innerSubtree[0] == 'definition'):
                        outputCommand = outputCommand + ' ' + 'define'
                    else:
                        outputCommand = outputCommand + ' ' + innerSubtree[0]
                elif(innerSubtree[1] == 'JJ'):
                    if(innerSubtree[0] == 'wiki' or innerSubtree[0] == 'locate'):
                        outputCommand = outputCommand + ' ' + innerSubtree[0]
    outputCommand = outputCommand.strip()
    print(outputCommand)
    return outputCommand


def runner():
    try:
        app.run()
    except:
        print("Rerunning")
        runner()


if __name__ == "__main__":
    runner()
