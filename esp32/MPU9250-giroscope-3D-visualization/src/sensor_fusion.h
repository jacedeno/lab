#pragma once

// Madgwick sensor fusion filter (6-DOF: accel + gyro)
// Produces a unit quaternion representing orientation.

#include <math.h>

class MadgwickFilter {
public:
    MadgwickFilter(float beta = 0.1f, float sampleFreq = 200.0f)
        : _beta(beta), _sampleFreq(sampleFreq),
          _q0(1.0f), _q1(0.0f), _q2(0.0f), _q3(0.0f) {}

    void update(float gx, float gy, float gz, float ax, float ay, float az) {
        float q0 = _q0, q1 = _q1, q2 = _q2, q3 = _q3;

        // Rate of change from gyroscope
        float qDot1 = 0.5f * (-q1 * gx - q2 * gy - q3 * gz);
        float qDot2 = 0.5f * ( q0 * gx + q2 * gz - q3 * gy);
        float qDot3 = 0.5f * ( q0 * gy - q1 * gz + q3 * gx);
        float qDot4 = 0.5f * ( q0 * gz + q1 * gy - q2 * gx);

        // Compute feedback only if accelerometer measurement valid
        float aNorm = sqrtf(ax * ax + ay * ay + az * az);
        if (aNorm > 0.0f) {
            // Normalize accelerometer measurement
            float recipNorm = 1.0f / aNorm;
            ax *= recipNorm;
            ay *= recipNorm;
            az *= recipNorm;

            // Auxiliary variables to avoid repeated arithmetic
            float _2q0 = 2.0f * q0;
            float _2q1 = 2.0f * q1;
            float _2q2 = 2.0f * q2;
            float _2q3 = 2.0f * q3;
            float _4q0 = 4.0f * q0;
            float _4q1 = 4.0f * q1;
            float _4q2 = 4.0f * q2;
            float _8q1 = 8.0f * q1;
            float _8q2 = 8.0f * q2;
            float q0q0 = q0 * q0;
            float q1q1 = q1 * q1;
            float q2q2 = q2 * q2;
            float q3q3 = q3 * q3;

            // Gradient descent corrective step
            float s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay;
            float s1 = _4q1 * q3q3 - _2q3 * ax + 4.0f * q0q0 * q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az;
            float s2 = 4.0f * q0q0 * q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az;
            float s3 = 4.0f * q1q1 * q3 - _2q1 * ax + 4.0f * q2q2 * q3 - _2q2 * ay;

            // Normalize step magnitude
            recipNorm = 1.0f / sqrtf(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3);
            s0 *= recipNorm;
            s1 *= recipNorm;
            s2 *= recipNorm;
            s3 *= recipNorm;

            // Apply feedback step
            qDot1 -= _beta * s0;
            qDot2 -= _beta * s1;
            qDot3 -= _beta * s2;
            qDot4 -= _beta * s3;
        }

        // Integrate rate of change to yield quaternion
        float dt = 1.0f / _sampleFreq;
        q0 += qDot1 * dt;
        q1 += qDot2 * dt;
        q2 += qDot3 * dt;
        q3 += qDot4 * dt;

        // Normalize quaternion
        float recipNorm = 1.0f / sqrtf(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
        _q0 = q0 * recipNorm;
        _q1 = q1 * recipNorm;
        _q2 = q2 * recipNorm;
        _q3 = q3 * recipNorm;
    }

    float w() const { return _q0; }
    float x() const { return _q1; }
    float y() const { return _q2; }
    float z() const { return _q3; }

private:
    float _beta;
    float _sampleFreq;
    float _q0, _q1, _q2, _q3;
};
