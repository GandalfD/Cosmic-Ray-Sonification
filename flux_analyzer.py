import matplotlib.pyplot as plt
import numpy as np
import time
import pyaudio
from miditime.miditime import MIDITime
import wave

# constants
SMP_RATE = 44100
p = pyaudio.PyAudio()


class Flux:

    def __init__(self, path):
        self.time_list = []
        self.flux_list = []

        self.sound = np.empty(1)

        with open(path, "r") as flux_file:
            lines = flux_file.readlines()

        first_date_check = True
        for line in lines:
            if line[0] == "#":  # skip this line, no data
                continue
            elif first_date_check:
                self.first_date = time.strptime(
                    line[0:19], "%m/%d/%Y %H:%M:%S")
                self.first_day = self.first_date.tm_mday
                first_date_check = False

            date = time.strptime(line[0:19], "%m/%d/%Y %H:%M:%S")

            total_hours = (date.tm_mday - self.first_day) * 24

            # grab the utc time in hours
            self.time_list.append(
                float(total_hours + date.tm_hour + (date.tm_min / 60)))
            # grab the flux reading in events/m^2/minute
            self.flux_list.append(float(line[20:line.find(" ", 20)]))

        # creates plot based off of flux data
    def create_plot(self, ymin=0, ymax=0, trend=False):
        lines = plt.plot(self.time_list, self.flux_list, "o")
        # lines = plt.plot(self.bless[0], self.bless[1])
        # lines = plt.plot(self.bless[0], self.bless[2])

        if ymin != 0 or ymax != 0:
            plt.ylim(ymin, ymax)

        if trend is True:
            z = np.polyfit(lines[0].get_data()[0], lines[0].get_data()[1], 1)
            p = np.poly1d(z)
            plt.plot(lines[0].get_data()[0], p(lines[0].get_data()[0]), "r--")
            print("Trend Line: ", "y=%.6fx+(%.6f)" % (z[0], z[1]))

        plt.xlabel("Time Past " +
                   time.strftime("%m/%d/%Y", self.first_date) + " Hours")
        # plt.ylabel("Flux (events/$m^2$/minute)")
        plt.ylabel("Temperature (°C)")
        plt.show(block=True)

    # sonify with each flux count as one sine tone
    def sonify_single_tone(self):
        data_sound = []

        for flux in self.flux_list:

            sample = (np.sin(2 * np.pi * np.arange(SMP_RATE * 0.15)
                             * flux / 10 / SMP_RATE)).astype(np.float32)

            data_sound.append(sample)

        print("Setting up sound")
        self.sound = np.asarray(data_sound)

        print("Sound Data: ", self.sound)
        print("Sound Data Length: ", len(self.sound))

    # def sonify_gradual_tone(self):
    #     data_sound = []
    #
    #     for i, flux in enumerate(self.flux_list):
    #         # if its the last index or first index, no graduation required
    #         if i == len(self.flux_list) - 1 or i == 0:
    #             data_sound.append((np.sin(2 * np.pi * np.arange(SMP_RATE * 0.2)
    #                                       * flux / 10 / SMP_RATE)).astype(np.float32))
    #             continue
    #
    #         base = self.flux_list[i - 1] / 10
    #         freq_inc_amt = ((flux / 10) - base) / 30
    #
    #         # print(freq_inc_amt)
    #         for step in range(0, 30):
    #
    #             sound_inc = (np.sin(2 * np.pi * np.arange(SMP_RATE * 0.1)
    #                                 * (base + freq_inc_amt) / SMP_RATE)).astype(np.float32)
    #
    #             base += freq_inc_amt
    #             data_sound.append(sound_inc)
    #
    #         # print("----------------------------------------------")
    #
    #     self.sound = np.asarray(data_sound)
    #     print(data_sound)

    def read_blessings(self, path):
        self.bless = [[], [], []]  # time, pressure, temp
        day_num = 0

        for i in range(1, 8):
            lines = []

            with open(path + "_" + str(i) + ".out", "r") as file:
                lines = file.readlines()

            for line_num, line in enumerate(lines):
                # skip first line
                if line_num == 0:
                    continue

                line = line.replace("\t", " ")

                # get the time
                bless_time = float(line[0:line.find(" ")])
                if i != 1 and line_num == 1 and bless_time < 600:  # new day
                    day_num += 1

                self.bless[0].append((bless_time / 3600) + (day_num * 24))

                # get the pressure and temp
                pressure_index = self.__find_nth(line, " ", 11) + 1
                temp_index = self.__find_nth(line, " ", 12) + 1

                self.bless[1].append(
                    float(line[pressure_index: line.find(" ", pressure_index)]))
                self.bless[2].append(
                    float(line[temp_index: line.find(" ", temp_index)]))

            # print (self.bless[0])

    def __find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + len(needle))
            n -= 1
        return start

    def sonify_miditime(self):
        midi = MIDITime(120, "results/sound/01-03-snowstorm.mid", 5, 5, 3)
        c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

        # midi the flux
        flux_timed = [{"beat": self.hour_beat(t), "flux": f} for t, f in zip(
            self.time_list, self.flux_list)]
        flux_start = flux_timed[0]["beat"]

        flux_note_list = []
        flux_max = max(self.flux_list)
        flux_min = min(self.flux_list)

        for f in flux_timed:
            scale = midi.linear_scale_pct(flux_min, flux_max, f["flux"])
            note = midi.scale_to_note(scale, c_major)

            flux_note_list.append([
                f["beat"] - flux_start,
                midi.note_to_midi_pitch(note),
                100,
                1
            ])

        # compensate for extra blessing data
        blessed_adjusted = [[], [], []]  # time, pressure, temp
        for num, b in enumerate(self.bless[0]):
            if num % 12 == 0:  # rough estimate to go by every half hour
                blessed_adjusted[0].append(self.bless[0][num])
                blessed_adjusted[1].append(self.bless[1][num])
                blessed_adjusted[2].append(self.bless[2][num])

        print(len(blessed_adjusted[0]))
        print(len(self.flux_list))

        # midi the temperatures
        temp_timed = [{"beat": self.hour_beat(t), "temp": te} for t, te in zip(
            blessed_adjusted[0], blessed_adjusted[2])]
        temp_start = temp_timed[0]["beat"]

        temp_note_list = []
        temp_max = max(blessed_adjusted[2])
        temp_min = min(blessed_adjusted[2])

        for t in temp_timed:
            scale = midi.linear_scale_pct(temp_min, temp_max, t["temp"])
            note = midi.scale_to_note(scale, c_major)

            temp_note_list.append([
                t["beat"] - temp_start,
                midi.note_to_midi_pitch(note),
                50,
                1
            ])

        # midi the pressure
        pressure_timed = [{"beat": self.hour_beat(t), "pressure": p} for t, p in zip(
            blessed_adjusted[0], blessed_adjusted[1])]
        pressure_start = pressure_timed[0]["beat"]

        pressure_note_list = []
        pressure_max = max(blessed_adjusted[1])
        pressure_min = min(blessed_adjusted[1])

        for p in pressure_timed:
            scale = midi.linear_scale_pct(
                pressure_min, pressure_max, p["pressure"])
            note = midi.scale_to_note(scale, c_major)

            pressure_note_list.append([
                p["beat"] - pressure_start,
                midi.note_to_midi_pitch(note),
                50,
                1
            ])

        midi.add_track(flux_note_list)
        midi.add_track(temp_note_list)
        midi.add_track(pressure_note_list)

        midi.save_midi()

    def hour_beat(self, hours):
        beats_per_hour = 0.5
        return round(beats_per_hour * hours, 2)

    # plays sound based off of passed in list
    def play_sound(self):
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=SMP_RATE,
                        output=True)
        stream.write(self.sound.tobytes())
        stream.stop_stream()
        stream.close()

        # p.terminate()

    def write_wave(self, name):
        wf = wave.open("results/sound/" + name, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paFloat32
                                          ))
        wf.setframerate(SMP_RATE)

        wf.writeframes(self.sound.tobytes())

# sonify_single_tone()
# sonify_gradual_tone()

# change the magnitude
