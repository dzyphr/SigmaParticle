import ast
import subprocess
def getBytes(data: str):
    scalaOut = subprocess.Popen(["scala", "GetBytes", data], stdout=subprocess.PIPE, cwd="scala")
    JBytes, err = scalaOut.communicate() #TODO deal with err if there is one
    JBytesToStr =  JBytes.decode() #get the string format from the byte formatted output 
                            #(this does not mess with data value it is a formality for dealing with the Popen output)
    byteList = ast.literal_eval(JBytesToStr) #convert to a list of bytes that is interpreted corectly by jpype
    return byteList
