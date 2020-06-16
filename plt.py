import matplotlib.pyplot as plt

log_dir = "default.log"
type2c = {
    "request":"blue", 
    "reply" :"green", 
    "release" : "red"
}

plt.figure()
with open(log_dir, 'r') as f:
    cnt = 0
    node_num = 0
    for line in f:
        if "init" in line:
            plt.axhline(y=node_num, c = "black")
            node_num+=1
        if "recieve" in line:
            rec_node = int(line.split()[8])
            send_node = int(line.split()[-3])
            rec_t = int(line.split()[-1])
            msg = line.split('\'')[1]
            msg_type = msg.split(':')[1]
            send_t = int(msg.split(',')[0][1:])
            plt.plot([send_t,rec_t],[send_node,rec_node], c = type2c[msg_type], marker='.')
            plt.savefig("img/{}.png".format(cnt))
            cnt+=1
            