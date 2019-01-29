f_s = 360;    % Sample frequency in Hz
f_c = 45;     % Cut-off frequency in Hz
order = 4;    % Order of the butterworth filter

omega_c = 2 * pi * f_c;       % Cut-off angular frequency
omega_c_d = omega_c / f_s;    % Normalized cut-off frequency (digital)

[b, a] = butter(order, omega_c_d / pi);    % Design the Butterworth filter
disp('a = '); disp(a);                     % Print the coefficients
disp('b = '); disp(b);
H = tf(b, a, 1 / f_s);                     % Create a transfer function
bode(H);                                   % Show the Bode plot