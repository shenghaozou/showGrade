import glob, logging, re, os
import pyperclip, subprocess
KEY_PAT = re.compile("\[\[(.*?)(:.*?)?\]\]")
data = {}
index2key = []

def load(fileName):
    print("loading {}".format(fileName))
    with open(fileName, "r") as fr:
        t = fr.read()
        results = KEY_PAT.findall(t)
        fileName_ = fileName[:-4]
        data[fileName_] = {}
        data[fileName_]['text'] = t
        data[fileName_]['keyword'] = {}
        for result in results:
            defaultArg = result[1]
            if defaultArg and result[1][0] == ':':
                defaultArg = defaultArg[1:]
            newKey = ''.join(result)
            data[fileName_]['keyword'][newKey] = defaultArg
        print(data)

def loadAll():
    global data
    data = {}
    allShortCuts = glob.glob("*.txt")
    for f in allShortCuts:
        print("loading " + f)
        load(f)
    print("successfully load all.")

def list():
    i = 0
    for k in data:
        v = data[k]
        index2key.append(k)
        show = v['text']
        if len(show) >= 40:
            show = show[:40] + " ..."
        print("{index}. {key}: {content}".format(index = i, key = k, content = show))
        i += 1

def cb(k):
    entry = data[k]
    curStr = entry['text']
    print("Selected Text: " + curStr)
    for k in entry['keyword']:
        v = entry['keyword'][k]
        rp = input("set {key}: (default: {content})".format(key = k, content = v)).strip()
        if not rp:
            rp = v
        curStr = curStr.replace("[[{}]]".format(k), rp)
    print("Finish. Your current text: " + curStr)
    pyperclip.copy(curStr)
    print("Copied to Clipboard!")

if __name__ == "__main__":
    loadAll()
    while True:
        r = input("> ").strip()
        if r == "loadall":
            loadAll()
        elif r == "ls":
            list()
        elif r in data:
            print("find keyword in data.")
            cb(r)
        elif r.isdigit():
            print("try to process the index.")
            n = int(r)
            if n < len(index2key):
                cb(index2key[n])
        elif r == "touch":
            fn = input("file name(w/o txt): ").strip() + ".txt"
            subprocess.call(['vim', fn])
            load(fn)
            print("Success!")
        elif r == "rm":
            key = input("file name(w/o txt): ").strip()
            fn =  key + ".txt"
            if os.path.exists(fn):
                os.remove(fn)
                del data[key]
            else:
                print("file not exist")
        elif r == "quit":
            break
