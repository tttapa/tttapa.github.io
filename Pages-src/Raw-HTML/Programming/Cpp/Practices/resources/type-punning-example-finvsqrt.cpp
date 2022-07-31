float y = number;
long  i = *(long *) &y;                 // evil floating point bit level hacking
i       = 0x5f3759df - (i >> 1);        // what the fuck? 
y       = *(float *) &i;