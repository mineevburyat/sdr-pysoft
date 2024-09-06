MHZ = 1000000
def get_base_supbin(chan):
    chan = chan - 1
    db_12video_chan = [[item, (item-20), (item-6), (item+5), (item+19)] for item in range(960, 1540, 40)]
    return db_12video_chan[chan]

def find_video_chan(freq_list):
    db_base_ch = [item for item in range(960, 1540, 40)]
    channels = []
    for freq in freq_list:
        try:
            index = db_base_ch.index(freq)
            channels.append(index+1)
        except:
            continue
    
    if channels:
        print("info! there is a possibility of a video channel", channels)
        result = {}
        for channel in channels:
            sub_bin = get_base_supbin(channel)
            result[channel] = 0
            for freq in freq_list:
                if freq in sub_bin:
                    result[channel] += 1
            return result

    else:
        return {}
    
ch = find_video_chan([1240, 1234, 1259, 1220, 1245, 1225, 956, 1278, 1338, 999, 1419])
print(ch)