import subprocess



process = subprocess.Popen(['hackrf_sweep', '-w 1000000', '-1'], 
                         stdout=subprocess.PIPE,
                         text=True)
for line in iter(process.stdout.readline, ''):
    print(line)

# process = Popen(, 
#                 stdout=PIPE, 
#                 stderr=PIPE,
#                 encoding='utf-8')

# try:
#     while process.poll() is None:
#         # print(f'\r{run_str[indx]} {count_find} ({count_freq})', end='')
#         line = process.stdout.read()
#         # err = process.stderr.read()
#         print(line)
#         # print(err)
# except KeyboardInterrupt:
#     errs = process.stderr.readlines()
# finally:
#     process.kill()
   

# # for line in errs:
# #     print(line.strip())
# # try:
# #     for line in iter(process.stdout.readline, ''):
# #         print(line)
# # except:
# #     process.terminate()
# #     process.communicate()
# #     errs = process.stderr.readlines()
# #     process.kill()


