
#Defines the node class of the Huffman tree
class node(object):

    def __init__(self,value = None,left = None,right = None,father = None):
        self.value = value
        self.left = left
        self.right = right
        self.father = father

    def build_father(left,right):
    	n = node(value = left.value + right.value,left = left,right = right)
    	left.father = right.father = n
    	return n

    def encode(n):
    	if n.father == None:
    		return b''
    	if n.father.left == n:
    		return node.encode(n.father) + b'0'
    	else:
    		return node.encode(n.father) + b'1'

#Build Huffman tree
def build_tree(l):

	if len(l) == 1:
		return l
	sorts = sorted(l,key = lambda x:x.value,reverse = False)
	n = node.build_father(sorts[0],sorts[1])
	sorts.pop(0)
	sorts.pop(0)
	sorts.append(n)
	return build_tree(sorts)

def encode(echo):

	for x in node_dict.keys():
		ec_dict[x] = node.encode(node_dict[x])
		if echo == True:
			print(x)
			print(ec_dict[x])

def encodefile(inputfile):

	print("Starting encode...")
	f = open(inputfile,"rb")
	bytes_width = 1
	i = 0

	f.seek(0,2)
	count = f.tell() / bytes_width
	print(count)
	nodes = []
	buff = [b''] * int(count)
	f.seek(0)

	while i < count:
		buff[i] = f.read(bytes_width)
		if count_dict.get(buff[i], -1) == -1:
			count_dict[buff[i]] = 0
		count_dict[buff[i]] = count_dict[buff[i]] + 1
		i = i + 1
	print("Read OK")
	print(count_dict)
	for x in count_dict.keys():
		node_dict[x] = node(count_dict[x])
		nodes.append(node_dict[x])

	f.close()
	tree = build_tree(nodes)
	encode(False)
	print("Encode OK")

	head = sorted(count_dict.items(),key = lambda x:x[1] ,reverse = True)
	bit_width = 1
	print("head:",head[0][1])
	if head[0][1] > 255:
		bit_width = 2
		if head[0][1] > 65535:
			bit_width = 3
			if head[0][1] > 16777215:
				bit_width = 4
	print("bit_width:",bit_width)
	i = 0
	raw = 0b1
	last = 0
	name = inputfile.split('.')
	o = open(name[0]+".ys" , 'wb')
	name = inputfile.split('/')
	o.write((name[len(name)-1] + '\n').encode(encoding="bitstring"))	#Write the original file name
	o.write(int.to_bytes(len(ec_dict) ,2 ,byteorder = 'big'))		#Write out the number of nodes
	o.write(int.to_bytes(bit_width ,1 ,byteorder = 'big'))			#Write the code table byte width
	for x in ec_dict.keys():										#Encoding header
		o.write(x)
		o.write(int.to_bytes(count_dict[x] ,bit_width ,byteorder = 'big'))

	print('head OK')
	while i < count:												#Start compressing the data
		for x in ec_dict[buff[i]]:
			raw = raw << 1
			if x == 49:
				raw = raw | 1
			if raw.bit_length() == 9:
				raw = raw & (~(1 << 8))
				o.write(int.to_bytes(raw ,1 , byteorder = 'big'))
				o.flush()
				raw = 0b1
				tem = int(i  /len(buff) * 100)
				if tem > last:
					print("encode:", tem ,'%')						#Output compression schedule
					last = tem
		i = i + 1

	if raw.bit_length() > 1:										#Processing data of less than one byte at the end of the file
		raw = raw << (8 - (raw.bit_length() - 1))
		raw = raw & (~(1 << raw.bit_length() - 1))
		o.write(int.to_bytes(raw ,1 , byteorder = 'big'))
	o.close()
	print("File encode successful.")


if __name__ == '__main__':

	#Data initialization
	node_dict = {}			#The mapping between the original data and the encoding node is established to facilitate the encoding of the output data later
	count_dict = {}
	ec_dict = {}
	nodes = []
	inverse_dict = {}

	if input('(Enter 1 = Encoding the file) \Please enter the action you want to perform:') == '1':
		encodefile(input("Please enter the file you want to compress:"))
