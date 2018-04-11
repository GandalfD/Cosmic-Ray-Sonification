import flux_analyzer as flux

test = flux.Flux("raw_data/flux/snowstorm_flux.out")

# test.create_plot()
# test.sonify_single_tone()
# test.sonify_gradual_tone()
# test.write_wave("02-01.wav")
# test.create_plot(0, 6000)
test.read_blessings("raw_data/blessing/snowstorm")
# test.sonify_miditime()
# test.play_sound()
test.create_plot(trend=True)
