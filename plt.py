import matplotlib.pyplot as plt
import queue

log_dir = "default.log"
type2c = {
    "request":"blue", 
    "reply" :"green", 
    "release" : "orange",
    "use": "red"
}

q = queue.PriorityQueue()
fig, ax=plt.subplots()
with open(log_dir, 'r') as f:
    cnt = 0
    node_num = 0
    max_ts = 0
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
            q.put((send_t,rec_t,send_node,rec_node,msg_type))
            max_ts = max(max_ts, rec_t)
        if "enters" in line:
            u_send_node = int(line.split()[-5])
            u_send_t = int(line.split()[-1])
        if "leaves" in line:
            u_rec_node = int(line.split()[-5])
            u_rec_t = int(line.split()[-1])
            msg_type = "use"
            max_ts = max(max_ts, rec_t)
            q.put((u_send_t,u_rec_t,u_send_node,u_rec_node,msg_type))

for _ in range(max_ts):
    plt.axvline(x=_+1, ls='--', c='grey')

plt.yticks(list(range(node_num)))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

cnt = 0
plt.xlim([0,max_ts])
while not q.empty():
    data = q.get()
    send_t,rec_t,send_node,rec_node,msg_type = data[0],data[1],data[2],data[3],data[4]
    print(cnt,send_t,rec_t,send_node,rec_node,msg_type)
    # plt.plot([data[1],data[0]],[data[2],data[3]], c = type2c[msg_type], marker='.')
    c = type2c[msg_type]
    plt.arrow(send_t,send_node,rec_t-send_t,rec_node-send_node,
                width=0.01,
                head_width=0.1,
                head_length=0.3,
                length_includes_head=True, 
                fc=c, ec=c)
    plt.savefig("img/{}.png".format(cnt))
    cnt+=1
            