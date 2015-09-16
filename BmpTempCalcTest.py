adc_t = 519888
cal_t1 = 27504
cal_t2 = 26435
cal_t3 = -1000

var1 = (((adc_t >> 3) - (cal_t1 << 1)) * cal_t2) >> 11

print "%.4f" % (var1)

var2 = (((adc_t >> 4) - cal_t1) * ((adc_t >> 4) - cal_t1) >> 12) * cal_t3 >> 14

print "%.4f" % (var2)

t_fine = var1 + var2

print(t_fine)

T = (t_fine * 5 + 128) >> 8

print(T)
