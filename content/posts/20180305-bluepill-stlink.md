Title: Programming a Blue Pill board with the ST-LINK v2
Date: 2018-03-05 23:26
Tags: hardware, embedded, bluepill

I picked up a set of five [blue pill boards](http://wiki.stm32duino.com/index.php?title=Blue_Pill)
and a tiny ST-LINK V2 JTAG programmer from ebay. Total cost with shipping was
$19.36; it took just under two weeks for the boards to arrive from China. I
figured I should do the hello world of embedded systems programming and blink
an LED.

Of course, the first challenge is HTF to program these things... so, this
will cover how I got [*someone else's*](https://github.com/satoshinm/pill_blink/tree/master/bare-metal)
blinky program to run. Then, I'll start working on building out
my own. Half of the reason I got these boards was to do bare metal
programming again on something small and portable. The goal is to get
some sort of operating system (like, I dunno, maybe a Forth) running on
them via a serial interface. Maybe later I'll hook up some cool devices
or whatever to the I/O ports. Really, I just wanted to mess around with
embedded again with something cheap (so I can wipe it) that I can throw
in my bag.

The programmer ships with a programming cable with four connectors. The colours
on mine are (in order) black, white, grey, and purple. On my blue pills, if the
JTAG pins are facing me, the ground is on the far right; it makes sense to use
the black wire for that. So, I did. Then I connected the cables on the board in
order. The hookups are in pin-order on the board are:

* black: ground
* white: SWCLK
* grey: SWDIO
* purple: 3V3

Next, it's time to install the toolchain:

```
sudo apt-get install gcc-arm-none-eabi libstdc++-arm-none-eabi-newlib libnewlib-arm-none-eabi
```

Then, the programmer needs to be installed. I'm using
[texane's stlink](https://github.com/texane/stlink). There are
instructions in the repo, but in short, on my Ubuntu 17.10 system (I'm
using the N22 netbook):

```
sudo apt-get install cmake libusb-1.0.0-dev
git clone https://github.com/texane/stlink
cd stlink
make release
cd build/Release
sudo make install
ldconfig
```

Side note, I love (ha ha only serious) the use of make to bootstrap
cmake to bootstrap make.

I made a [skeleton](https://github.com/kisom/sandbox/tree/master/blue-pill/skeleton)
project. There are two key components right now: the linker script and the Makefile.
The linker script is pretty standard; I cribbed mine from the aforementioned project,
but I could have just read the [data sheet](http://www.st.com/content/ccc/resource/technical/document/datasheet/33/d4/6f/1d/df/0b/4c/6d/CD00161566.pdf/files/CD00161566.pdf/jcr:content/translations/en.CD00161566.pdf).

The Makefile is meant so that I only need to provide the name for the program
(it's assumed that the main source file shares the same basename as the output,
but this can be changed by removing the `OBJS +=...` line. Optionally, I can
supply other object files to include, too. Awesome sauce. The rest is a bunch
of stuff that I really only need to look up once and then copy-paste to every
new project. So, here's the Makefile:

```
# configurables
OBJS :=		
TARGET :=	blinky
OBJS +=		$(TARGET).o

# targets
ELF :=		$(TARGET).elf
BIN :=		$(TARGET).bin

# toolchain setup
ARMTC :=	arm-none-eabi
ARMCC :=	$(ARMTC)-gcc
CC :=		$(ARMCC)
LD :=		$(ARMCC)
ARMSIZE :=	$(ARMTC)-size
OBJCOPY :=	$(ARMTC)-objcopy

# compiler options
CPUFLAGS :=	-mcpu=cortex-m3 -mthumb
CFLAGS :=	-Wall -Wextra -Os -MD $(CPUFLAGS)
LDFLAGS :=	$(CPUFLAGS) -nostartfiles -Wl,-T,bluepill.ld
LDLIBS :=	-lc -lnosys

# programmer options
STARTMEM :=	0x8000000

# targets

.PHONY: all
all: $(BIN)

$(ELF): $(OBJS)
	$(ARMCC) $(LDFLAGS) -o $@ $(OBJS) $(LDLIBS)
	$(ARMSIZE) -A $@

$(BIN): $(ELF)
	$(OBJCOPY) -O binary $< $@

.PHONY: flash
flash: $(BIN)
	st-flash write $(BIN) $(STARTMEM)

.PHONY: erase
erase:
	st-flash erase

.PHONY: install
install: erase flash

.PHONY: clean
clean:
	rm -f *.o *.bin *.elf *.d *.map
```

So, for example, the skeleton-based blinky builds and works. I'm too
lazy to post photos, but here's a console dump:

```
kyle@molly:~/code/sandbox/blue-pill/blinky$ make clean all install
rm -f *.o *.bin *.elf *.d *.map
arm-none-eabi-gcc -Wall -Wextra -Os -MD -mcpu=cortex-m3 -mthumb   -c -o blinky.o blinky.c
arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -nostartfiles -Wl,-T,bluepill.ld -o blinky.elf  blinky.o -lc -lnosys
arm-none-eabi-size -A blinky.elf
blinky.elf  :
section           size        addr
.text              440   134217728
.comment            43           0
.ARM.attributes     51           0
Total              534


arm-none-eabi-objcopy -O binary blinky.elf blinky.bin
st-flash erase
st-flash 1.4.0-23-g1f18a18
2018-03-05T23:22:46 INFO common.c: Loading device parameters....
2018-03-05T23:22:46 INFO common.c: Device connected is: F1 Medium-density device, id 0x20036410
2018-03-05T23:22:46 INFO common.c: SRAM size: 0x5000 bytes (20 KiB), Flash: 0x20000 bytes (128 KiB) in pages of 1024 bytes
Mass erasing
st-flash write blinky.bin 0x8000000
st-flash 1.4.0-23-g1f18a18
2018-03-05T23:22:46 INFO common.c: Loading device parameters....
2018-03-05T23:22:46 INFO common.c: Device connected is: F1 Medium-density device, id 0x20036410
2018-03-05T23:22:46 INFO common.c: SRAM size: 0x5000 bytes (20 KiB), Flash: 0x20000 bytes (128 KiB) in pages of 1024 bytes
2018-03-05T23:22:46 INFO common.c: Attempting to write 440 (0x1b8) bytes to stm32 address: 134217728 (0x8000000)
Flash page at addr: 0x08000000 erased
2018-03-05T23:22:46 INFO common.c: Finished erasing 1 pages of 1024 (0x400) bytes
2018-03-05T23:22:46 INFO common.c: Starting Flash write for VL/F0/F3/F1_XL core id
2018-03-05T23:22:46 INFO flash_loader.c: Successfully loaded flash loader in sram
  1/1 pages written
2018-03-05T23:22:46 INFO common.c: Starting verification of write complete
2018-03-05T23:22:46 INFO common.c: Flash written and verified! jolly good!
kyle@molly:~/code/sandbox/blue-pill/blinky$ 
```

Okay, time to start writing a header file for this thing.
