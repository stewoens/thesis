from py2cfg.builder import CFGBuilder
import json
import os

#absolute_path = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/data"
absolute_path = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/py2cfg/examples/singletest"
name = "ninatest"
with open(f'{name}.json', 'w') as fjson:
    for root, dirs, files in os.walk(absolute_path):
        for file in files:
            with open(os.path.join(root, file), "r",encoding='cp437') as fpy:
                #print(fpy.name)
                cfg, mylist = CFGBuilder().build_from_file(name, fpy.name) #have second output of json info as dict
                if mylist is None:
                    print("ERROR: could not create entry: ", fpy.name)
                else:
                    json_object= json.dumps(mylist, indent=4)
                    fjson.write(json_object)
        
#cfg, mylist = CFGBuilder().build_from_file(name, './examples/loops-09-caesar-for.py') #have second output of json info as dict


#print(mylist)
#cfg.build_visual(name , 'pdf')

#write actual json file

            
# with open(f'{name}.json', 'w') as f:
#     json_object= json.dumps(mylist, indent=4)
#     f.write(json_object)