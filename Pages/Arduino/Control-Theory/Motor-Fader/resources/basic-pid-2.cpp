/// Very basic, mostly educational PID controller with derivative filter, output
/// clamping and integral anti-windup.
class PID {
  public:
    /* ... */

    /// Update the controller with the given position measurement `meas_y` and
    /// return the new control signal.
    float update(float reference, float meas_y) {
        // e[k] = r[k] - y[k], error between setpoint and true position
        float error = reference - meas_y;
        // e_f[k] = α e[k] + (1-α) e_f[k-1], filtered error
        float ef = alpha * error + (1 - alpha) * old_ef;
        // e_d[k] = (e_f[k] - e_f[k-1]) / Tₛ, filtered derivative
        float derivative = (ef - old_ef) / Ts;
        // e_i[k+1] = e_i[k] + Tₛ e[k], integral
        float new_integral = integral + error * Ts;

        // PID formula:
        // u[k] = Kp e[k] + Ki e_i[k] + Kd e_d[k], control signal
        float control_u = kp * error + ki * integral + kd * derivative;

        // Clamp the output
        if (control_u > max_output)
            control_u = max_output;
        else if (control_u < -max_output)
            control_u = -max_output;
        else // Anti-windup
            integral = new_integral;
        // store the state for the next iteration
        old_ef = ef;
        // return the control signal
        return control_u;
    }

  private:
    float kp, ki, kd, alpha, Ts;
    float max_output = 255;
    float integral = 0;
    float old_ef = 0;
};