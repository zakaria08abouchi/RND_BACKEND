j=0
l=[1,6,9,3,2,14,16,11]
k=0
while k < len(l)-1 :
    j=0
    for i in l:
        
        print(j,l)
        if l[j] >= l[j+1]:
            j+=1
        else:
            x=l[j+1]
            l[j+1]=l[j]
            l[j]=x
    k+=1

print(l) 
