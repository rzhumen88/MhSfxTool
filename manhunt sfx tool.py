#by rzhumen88 for 'NoData' dub team
import os
from time import gmtime, strftime

def log(mes, only_write=False):
    logs = open("logs.txt", "a")
    if type(mes) is str:
        logs.write(mes+"\n")
        if not only_write: print(mes)
        logs.close()
        
def rmmtd():
    pos = 0
    offsets = [0,]
    log("Searching in sfx.raw...")
    with open("sfx.raw", "rb") as RAW:
        RAW = RAW.read()
        while RAW.find(b'LIST', pos, len(RAW)) > 0:
            pos = RAW.find(b'LIST', pos, len(RAW))
            offsets.append(pos)
            pos = pos + 4
        log(f"Found {len(offsets)} pieces of metadata.")
        i = 0
        j = 0
    if len(offsets) > 0:
        with open("sfx.raw", "wb") as newRAW:
            for i in range(0, len(offsets)):
                newRAW.write(RAW[j:offsets[i]])
                for k in range(0, 52):
                    newRAW.write(b'\x00')
                j = offsets[i]+52
            newRAW.write(RAW[j:])
            log("Done!")
    
def build():
    try:
        if not os.path.isdir("extracted/"):
            log("ERROR: Can't find extracted files.")
            input()
            exit()
        log("Parsing sfx.lst...")
        SFXLIST = open('sfx.lst', 'r').read().split('\n') #в этом файле названия аудиофайлов по порядку

        SFXFILENAMES = []
        SFXLENLIST = []
        ADDCHUNK = []
        i = 0
        offset = 0
        startoffset = 0
        CHUNK = 2048

        while i <= len(SFXLIST):
            i += 1
            try:
                if SFXLIST[i][-4:] == '.WAV':
                    line = SFXLIST[i].replace("\\", "/")
                    line = line[4:]
                    SFXFILENAMES.append(line)
            except: pass 
        log(f"Parsed {len(SFXFILENAMES)} WAV files!")

        SFXLIST.clear()

        log("Parsing WAV files for lenght and Hz, it might take a while...")
        with open("sfx.sdt", "wb") as SDT:   
            for filename in SFXFILENAMES:
                with open("extracted/"+filename, "rb") as f:
                        f = f.read()
                        wavLen = len(f)-44
                        origLen = wavLen
                        #CALCULATING CHUNKS
                        i = 0
                        while i < wavLen:
                            i = i + CHUNK
                        ADDCHUNK.append(i - wavLen)
                        wavLen = i
                        
                        i = 0
                        Hz = f[24:28]
                        SFXLENLIST.append(wavLen)
                        SDT.write(int.to_bytes(startoffset, length=4, byteorder='little'))
                        SDT.write(int.to_bytes(wavLen, length=4, byteorder='little'))
                        SDT.write(Hz)
                        SDT.write(b'\x00'*4)
                        SDT.write(int.to_bytes(origLen, length=4, byteorder='little'))
                        startoffset = startoffset + wavLen
                        
        log("sfx.sdt created!")
        log("Creating SFX.RAW, it might also take a while...")
    except Exception as e:
       input(f'ERROR: {type(e)}')
       input()
    with open("SFX.RAW", "wb") as RAW:
        i = 0
        try:
            for filename in SFXFILENAMES:
                with open("extracted/"+filename, "rb") as f:
                    f = f.read()
                    RAW.write(f[44:])
                    RAW.write(b'\x00'*ADDCHUNK[i])
                    i += 1
                    log(f"[{i}/{len(SFXFILENAMES)}]\tEXTRACTED/{filename} injected!")
        except Exception as e: log("FUCKUP on"+filename)
        

    log("All done!")
    
def extract():
    log("Parsing sfx.lst...")
    SFXLIST = open('sfx.lst', 'r').read().split('\n')
    i = 0
    SFXFILENAMES = []
    while i <= len(SFXLIST):
        i += 1
        try:
            if SFXLIST[i][-4:] == '.WAV':
                line = SFXLIST[i].replace("\\", "/")
                line = line[4:]
                SFXFILENAMES.append(line)
        except: pass 
    log(f"Parsed {len(SFXFILENAMES)} WAV files!")

    SFXLIST.clear()

    log("Parsing WAV files for lenght and Hz, it might take a while...")
    fileNum = 0
    with open("sfx.sdt", "rb") as SDT:
        SDT = SDT.read()
        with open("SFX.RAW", "rb") as SFX:
            SFX = SFX.read()
            for fileNum in range(0, len(SFXFILENAMES)):
                OFFSET = int.from_bytes(SDT[20*fileNum:20*fileNum+4], 'little')
                LENGTH = int.from_bytes(SDT[20*fileNum+4:20*fileNum+8], 'little')
                Hz = SDT[20*fileNum+8:20*fileNum+12]
                byteRate = int.from_bytes(SDT[20*fileNum+8:20*fileNum+12], 'little')*2
                Fdirectory = "extracted//"+SFXFILENAMES[fileNum]
                directory = Fdirectory
                while directory[-1] != "/":
                    directory = directory[:-1]
                if not os.path.isdir(directory):
                    os.makedirs(directory, exist_ok=True)
                try:
                    with open(Fdirectory, "wb") as WAV:
                        WAV.write(b'RIFF')
                        WAV.write(int.to_bytes(LENGTH+84, length=4, byteorder='little'))
                        WAV.write(b'\x57\x41\x56\x45\x66\x6D\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00') #WAVEfmt
                        WAV.write(Hz)
                        WAV.write(int.to_bytes(byteRate, length=4, byteorder='little'))
                        WAV.write(b'\x02\x00\x10\x00\x64\x61\x74\x61') #data
                        WAV.write(int.to_bytes(LENGTH, length=4, byteorder='little'))
                        WAV.write(SFX[OFFSET:OFFSET+LENGTH])
                except FileExistsError:
                    os.remove(directory)
                except Exception as e:
                    log(f'ERROR: {type(e)}')
                    break
                
    input("All done!") 

    
##start
log(strftime("%a, %d %b %Y %H:%M:%S", gmtime()), only_write=True)
log(" ")
log("Manhunt SFX tool by rzhumen88")
log("To extract type: e")
log("To build type: b")
log("To remove sony vegas metadata from the SFX.RAW type: rm metadata")
log("To make backups type: bck")
log("To back to the backups type: undo")
while True:
    func = input()
    if not os.path.isfile("sfx.lst") or not os.path.isfile("SFX.RAW") or not os.path.isfile("sfx.sdt"):
        log("ERROR: Can't find SFX files, drag this script in")
        log("Manhunt/audio/PC/SFX directory and try again.")
        input()
        break
    match func:
        case "e":
            extract()
            
        case "b":
            build()
            
        case "bck":
            log("Wait...")
            try:
                os.system('copy sfx.raw sfx.raw.bck')
                os.system('copy sfx.sdt sfx.sdt.bck')
            except: log("Something went wrong")
            finally: log("Copying done!")
            
        case "undo":
            log("Wait...")
            if not os.path.isfile("sfx.raw.bck") and os.path.isfile("sfx.sdt.bck"):
                log("Can't find sfx.raw.bck or sfx.sdt.bck")
            else:
                os.remove("sfx.raw")
                os.remove("sfx.sdt")
                os.system('copy sfx.raw.bck sfx.raw')
                os.system('copy sfx.sdt.bck sfx.sdt')
                log("Backups restored!")
        case "rm metadata":
            rmmtd()
        case _:
            log("What?")

        
