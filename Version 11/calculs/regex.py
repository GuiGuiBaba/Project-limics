import re

def is_parenthese_diff(regex):
    """
    Check if there is a different number of open and close brackets in the string.
    
    Parameters : 
    regex (str) : string containing a regex. 
    
    Return :
    (boolean) : return true if the number of open and close brackets are equal. 
    """
    i1=0
    i2=0
    for char in regex : 
        if char=="(":i1+=1
        elif char==")":i2+=1
    if not (i1-i2==0):return True
    else :return False

def generate_regex(words):
    """
    Create a regex from the words in input.
    
    Parameters : 
    words (list) : list containing the different words to transform into a regex. 
    
    Return :
    (regex) 
    """
    regex="("
    connectors=["+","+?"]
    inOr=False
    
    for i,word in enumerate(words):
        if word in connectors or word.startswith("..."): 
            #a - closing
            regex+=")"
            if inOr:
                regex+="?"
                inOr=False 
            #b - creating    
            if word=="+": 
                regex+="\s"  
            elif word=="+?": 
                regex+="\s?"
                inOr=True
            elif word.startswith("..."):
                x = int(word[3:])
                regex+=f"[^.?!]{{0,{x}}}"
            regex+="("
            
        elif word=="/":
            regex+="|"
        else : 
            regex+=word
            
    if inOr: regex+=')?'            
    if is_parenthese_diff(regex):regex+=")"
    regex = r"\b"+"("+regex+")"+r"\b"
    
    return(re.compile(regex, flags = re.UNICODE | re.DOTALL))