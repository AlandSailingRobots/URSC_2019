################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/I2C_Sender.cpp \
../src/csv_log.cpp \
../src/gps.cpp \
../src/nmea.cpp \
../src/pid.cpp \
../src/pid_run.cpp \
../src/position_logger.cpp \
../src/roboboatfinal.cpp \
../src/rpi_cmps12.cpp \
../src/sail_lookup.cpp \
../src/serial.cpp 

OBJS += \
./src/I2C_Sender.o \
./src/csv_log.o \
./src/gps.o \
./src/nmea.o \
./src/pid.o \
./src/pid_run.o \
./src/position_logger.o \
./src/roboboatfinal.o \
./src/rpi_cmps12.o \
./src/sail_lookup.o \
./src/serial.o 

CPP_DEPS += \
./src/I2C_Sender.d \
./src/csv_log.d \
./src/gps.d \
./src/nmea.d \
./src/pid.d \
./src/pid_run.d \
./src/position_logger.d \
./src/roboboatfinal.d \
./src/rpi_cmps12.d \
./src/sail_lookup.d \
./src/serial.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: Cross G++ Compiler'
	g++ -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


