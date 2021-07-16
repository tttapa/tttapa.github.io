#include <cmath>

/// Very basic, mostly educational PID controller with derivative filter.
class PID {
  public:
    /// @param  kp  Proportional gain   @f$ K_p @f$
    /// @param  ki  Integral gain       @f$ K_i @f$
    /// @param  kd  Derivative gain     @f$ K_d @f$
    /// @param  fc  Cutoff frequency    @f$ f_c @f$ of derivative filter in Hz
    /// @param  Ts  Controller sampling time    @f$ T_s @f$ in seconds
    /// The derivative filter can be disabled by setting `fc` to zero.
    PID(float kp, float ki, float kd, float fc, float Ts)
        : kp(kp), ki(ki), kd(kd), alpha(calcAlphaEMA(fc * Ts)), Ts(Ts) {}

    /// Compute the weight factor α for an exponential moving average filter
    /// with a given normalized cutoff frequency `fn`.
    static float calcAlphaEMA(float fn);

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

        // store the state for the next iteration
        integral = new_integral;
        old_ef = ef;
        // return the control signal
        return control_u;
    }

  private:
    float kp, ki, kd, alpha, Ts;
    float integral = 0;
    float old_ef = 0;
};

float PID::calcAlphaEMA(float fn) {
    if (fn <= 0)
        return 1;
    // α(fₙ) = cos(2πfₙ) - 1 + √( cos(2πfₙ)² - 4 cos(2πfₙ) + 3 )
    const float c = std::cos(2 * float(M_PI) * fn);
    return c - 1 + std::sqrt(c * c - 4 * c + 3);
}
