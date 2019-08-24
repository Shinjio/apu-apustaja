from utils import urban_define, urban_parse_definition

defs = urban_define('tsundere')
if defs:
	print('"Tsundere" means:')
	defn = defs['definitions'][0]
	owo = ('{i}: {defn}'.format(i=1, defn=defn['definition']))
	print(owo)



#for i, defn, in enumerate(defs['definitions']): #era per il debug