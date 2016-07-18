#-*- coding: utf-8 -*-

import codecs
import re
import os

class settings():
    in_folder = './in/Year Walk/yearwalk_Data/Managed/'
    out_folder = './out/Year Walk/'
    assembly_name = 'Assembly-CSharp.il'

def read_file(filename):
    f = codecs.open(os.path.join(settings.in_folder, filename),'rb','utf-16')
    data = f.read()
    f.close()
    return data
    
def filter_string(st):
    #remove "\n + "
    r = re.compile(r'\"\s+\+\s\"',re.UNICODE)
    s = r.sub(r'',st)
    #remove start "
    r = re.compile(r'^\s*?\"',re.UNICODE)
    s = r.sub(r'',s)
    #remove end "
    r = re.compile(r'\"\n?\s*?$',re.UNICODE)
    s = r.sub(r'',s)
    return s
    
def filter_bytearray(bt):
    #http://regexr.com?38fsl
    r = re.compile(r'\/\/.+?$\s*',re.UNICODE|re.MULTILINE)
    bt = r.sub(r'',bt)
    
    r = re.compile(r'\(|\)|bytearray|\\|r|n',re.UNICODE)
    bt = r.sub(r'',bt)  
    #E9
    #bt = re.sub(r'E9','65',bt)
    bt = re.sub(r'\s{2,}',' ',bt,re.UNICODE).strip()
    
    b = bytearray.fromhex(bt)
    bt = bytes(b[:]).decode('utf-16')
    bt = bt.replace(u'\u2019',u'\'')
    bt = bt.replace(u'\n',u'\\n')
    return bt
    
def sortByIndex(index_list):
        return index_list[0]
    
def parse_assembly(assembly):
    extracted_list = []
    #all "..."
    reg1 = r'SGLocalization\:\:TEXT\s+?IL_\w+?:\s+?ldc.i4(?:.\w)?(?:\s+?\w+?)?\s+?IL_\w+?:\s+?ldstr\s+?(".+?")\s+?IL_\w+?:\s+?stelem.ref'
    r = re.compile(reg1, re.UNICODE|re.MULTILINE)
    s = r.finditer(assembly)
    for match in s:
        res = [match.start(1),match.end(1),filter_string(match.group(1))]
        extracted_list.append(res)

    #all "..." + "..." + "..."
    reg2 = r'SGLocalization\:\:TEXT\s+?IL_\w+?:\s+?ldc.i4(?:.\w)?(?:\s+?\w+?)?\s+?IL_\w+?:\s+?ldstr\s+?(".*"(?:\s+?\+\s".*"\s+?)+)\s+?IL_\w+?:\s+?stelem.ref'
    r = re.compile(reg2, re.UNICODE|re.MULTILINE)
    s = r.finditer(assembly)
    for match in s:
        res = [match.start(1),match.end(1),filter_string(match.group(1))]
        extracted_list.append(res)
    
    #bytearray
    reg3 = r'SGLocalization\:\:TEXT\s+?IL\w+?:\s+?ldc.i4(?:.\w)?(?:\s+?\w+?)?\s+?IL\w+?:\s+?ldstr\s+?(bytearray\s+?\((?:(?:\s*?.+?)\/\/.+?)+)\s+?IL\w+?:\s+?stelem.ref'
    r = re.compile(reg3, re.UNICODE|re.MULTILINE)
    s = r.finditer(assembly)
    for match in s:
        res = [match.start(1),match.end(1),filter_bytearray(match.group(1)),'b']
        extracted_list.append(res)

    #extracted_list.sort(key=sortByIndex)
    
    return extracted_list
    
def save_to_file(extracted_list):
    coords_file = 'assembly_coords'
    out_file = 'assembly_text'
    
    f = codecs.open(os.path.join(settings.out_folder,coords_file),'wb','utf-16')
    for line in extracted_list:
        f.write(str(line[0])+' '+str(line[1])+' ')
        if len(line) == 4:
            f.write(' '+line[3])
        f.write('\n')
    f.close()

    f = codecs.open(os.path.join(settings.out_folder,out_file),'wb','utf-16')
    for line in extracted_list:
        f.write(line[2]+'\n')
    f.close()

#hex(ord('я'))[2:].upper()
#'    '

def run():
    assembly = read_file(settings.assembly_name)
    extracted_list = parse_assembly(assembly)
    save_to_file(extracted_list)
    
if __name__ == "__main__":
    run()