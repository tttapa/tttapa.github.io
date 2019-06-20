[signal,f_s] = audioread('telegraph_road_original.wav');

alpha = 0.25;   % Filter factor of 1/4

b = alpha;            % Coefficients of the numerator of the transfer function
a = [1,-(1-alpha)];   % Coefficients of the denominator of the transfer function
filtered = filter(b,a,signal);   % Filter the signal

audiowrite('telegraph_road_filtered.wav',filtered,f_s);