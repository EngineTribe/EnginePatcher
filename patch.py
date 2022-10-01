#!/usr/bin/python
import yaml, math

package_orig=input('输入原始文件名 (libyoyo.so / SMM_WE.exe): ')
codec="utf-8"
locale_file=input('输入语言文件名: (CN.yaml / ES.yaml / EN.yaml) ')
tokens_file="tokens.json"
platform=input('输入平台代号 (PC代表电脑, MB代表安卓): ')

print("SMM:WE 引擎部落补丁程序")
print("By YidaozhanYa")
whitelist=yaml.load(open('whitelist.yaml'),Loader=yaml.FullLoader)['whitelist']
package=open(package_orig,"rb").read()
locale=yaml.load(open('locales/'+locale_file),Loader=yaml.FullLoader)
for str in locale:
    str_original=str
    str_replace=locale[str]
    if len(str_original.encode(codec))<len(str_replace.encode(codec)):
        print(str_replace+' 字符串的长度超出要求')
        exit()
    elif len(str_original.encode(codec))==len(str_replace.encode(codec)):
        if str_original in whitelist:
            print("替换全部 "+ str_original)
            package=package.replace(bytes(str_original,codec),bytes(str_replace,codec))
        else:
            print("替换一个 "+ str_original)
            package=package.replace(bytes(str_original,codec),bytes(str_replace,codec),1)
    elif len(str_original.encode(codec))>len(str_replace.encode(codec)):
        space_count=(len(str_original.encode(codec))-len(str_replace.encode(codec)))/2
        if str_original in whitelist:
            print("替换全部 "+ str_original)
            package=package.replace(bytes(str_original,codec),bytes(" "*math.ceil(space_count)+str_replace+" "*math.floor(space_count),codec))
        else:
            print("替换一个 "+ str_original)
            package=package.replace(bytes(str_original,codec),bytes(" "*math.ceil(space_count)+str_replace+" "*math.floor(space_count),codec),1)
tokens=yaml.load(open('tokens.yaml'),Loader=yaml.FullLoader)
for key in tokens:
    token = tokens[key]
    if platform=="PC":
        print("替换 "+ token + " 令牌 for PC")
        package=package.replace(bytes(token,codec),bytes('SMMWEPC'+locale_file.split('.')[0],codec),1)
    elif platform=="MB":
        print("替换 "+ token + " 令牌 for MB")
        package=package.replace(bytes(token,codec),bytes('SMMWEMB'+locale_file.split('.')[0],codec),1)
print("正在写出文件...")
if 'libyoyo' in package_orig:
    package_out='libyoyo.so.patched'
else:
    package_out='SMM_WE_EngineTribe_'+locale_file.split('.')[0]+'.exe'
f=open(package_out,"wb")
f.write(package)
f.close()
print("打补丁完成!")
