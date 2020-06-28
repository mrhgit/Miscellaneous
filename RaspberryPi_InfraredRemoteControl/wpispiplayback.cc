/*
gcc -lstdc++ -lwiringPi wpispiplayback.cc 
sudo sh -c "echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
sudo ./a.out
sudo sh -c "echo ondemand > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
 
Sends custom codes out over the SPI at a controlled rate to control device via an infrared diode.

*/

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <string>
#include <wiringPi.h>
#include <wiringPiSPI.h>

#include <signal.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <cstring>

using namespace std;
 
#define DELAYOFFSET 0
#define SPICHANNEL 1
// SPISPEED = 38000 * 2
#define SPISPEED 76000
#define REPEAT_COUNT 1

unsigned int bytePtr = 0;
unsigned int bitPtr = 0;

#define DATABUFSIZE 4096
#define usecPerBit (26.31578947/2)

unsigned char * databuf;

bool exit_condition = false;

void ctrlc_handler(int s){
  exit_condition = true;
}

void clearSig() {
  memset(databuf, 0x00, DATABUFSIZE);
  bytePtr = 0;
  bitPtr = 0;
}

void filldata(int usec, unsigned char fill){
  if (bytePtr>=DATABUFSIZE) return; 

  int cnt = usec / usecPerBit / 2; // total number of bit cycles represented by usec

  // Fill in any previous hole
  if (bitPtr > 0) {
    while ((bitPtr < 8) && (cnt > 0)){
      databuf[bytePtr] |= (fill & 0x3) << (8-bitPtr);
      bitPtr += 2;
      cnt -= 1;
    }
    if (bitPtr==8){
      bytePtr++;
      bitPtr = 0;
    }
  }

  int cnt8 = cnt / 4;
  int cntbit = cnt % 4;

  for (int i=0; i < cnt8; i++) {
    databuf[bytePtr++] = fill; // 10101010
    if (bytePtr>=DATABUFSIZE) return;
  }

  for (int i=0; i < cntbit; i++) {
    databuf[bytePtr] |= (fill & 0x03) << (8-bitPtr);
    bitPtr += 2;
  }
}

void pulseIR(int usec){
  filldata(usec, 0xAA);
}

void spacer(int usec){
  filldata(usec, 0x00);
}



void LGCode(int num) {
  const int ontime = 450;
  const int offtime = 750;//750;
  const int longofftime = 1500;
  for (int i=0; i < (num-1); i++){
    pulseIR(ontime);
    spacer(offtime);
  }

  pulseIR(ontime);  spacer(longofftime);
}


void LGHeader() {
  clearSig();
  pulseIR(9300); spacer(4500);
  LGCode(1);
  LGCode(4);
  
}

void AC_OFF() {
  LGHeader();
  LGCode(4);
  LGCode(1);
  LGCode(12);
  LGCode(2);
  LGCode(4);
  LGCode(1);
}

void AC_ONHEAT76() {
  LGHeader();
  
  LGCode(9);
  LGCode(3);
  LGCode(3);
  LGCode(3);
  LGCode(3);
  LGCode(2);
  LGCode(1);
  LGCode(1);
  LGCode(1);
  LGCode(1);
}

void AC_ONAC74() {
  LGHeader();
  
  LGCode(12);
  LGCode(5);
  LGCode(3);
  LGCode(1);
  LGCode(3);
}

void setCPUMode(string mode) {
   int fd = open("/sys/devices/system/cpu/cpufreq/policy0/scaling_governor", O_WRONLY);
    if (fd == -1) {
        perror("Unable to open /sys/devices/system/cpu/cpufreq/policy0/scaling_governor");
        exit(1);
    }

    if (write(fd, mode.c_str(), mode.length()) != mode.length()) {
        perror("Error writing to /sys/devices/system/cpu/cpufreq/policy0/scaling_governor");
        exit(1);
    }

    close(fd);
}

int main(int argc, char **argv)
{
    void (*remoteFunction)() = NULL;
    if (argc < 2) {
      printf("No remote control signal function specified.\n");
      return 1;
    }
    string command = argv[1];
    if (command=="AC_ONHEAT76") {
      printf("Turning on AC - Heat 76 Degrees\n");
      remoteFunction = AC_ONHEAT76;
    }
    else if (command=="AC_OFF") {
      printf("Turning off AC\n");
      remoteFunction = AC_OFF;
    }
    else if (command=="AC_ONAC74") {
      printf("Turning on AC - AC 74 Degrees\n");
      remoteFunction = AC_ONAC74;
    }
    else {
      printf("Invalid remote control signal function specified\n");
      return 1;
    }
    setCPUMode("performance");
  
    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = ctrlc_handler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, NULL);

    databuf = (unsigned char *)malloc(DATABUFSIZE);
    piHiPri(0);
    wiringPiSetup();
    wiringPiSPISetup (SPICHANNEL, SPISPEED);
    
    //while (1) {
    for (int n=0; n < REPEAT_COUNT; n++) {
      remoteFunction();
      wiringPiSPIDataRW (SPICHANNEL, databuf, DATABUFSIZE) ;

      sleep(1);
      if (exit_condition) break;
    }
    printf("Freeing memory...\n");
    free(databuf);
    
    setCPUMode("ondemand");

    printf("Goodbye\n");
    return 0;
}
