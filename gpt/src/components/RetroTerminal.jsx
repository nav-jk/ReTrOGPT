// src/components/RetroTerminal.jsx
import React from 'react';
import {
  Terminal,
  useEventQueue,
  textLine,
  textWord,
  commandWord,
} from 'crt-terminal';

const bannerText = `
********** SYSTEM BOOT **********
Starting BIOS...
Initializing Components...
Please Wait...
LOADING SYSTEM...
-------------------------------
| CPU: Intel(R) Pentium(TM)   |
| Memory: 8MB DRAM            |
| Graphics: VGA               |
| Storage: 250MB HDD          |
-------------------------------
READY.
`;

export default function RetroTerminal() {
  const eventQueue = useEventQueue();
  const { print } = eventQueue.handlers;

  const handleCommand = async (command) => {
    // Print user's input
    print([
      textLine({
        words: [
          textWord({ characters: 'You: ' }),
          commandWord({ characters: command, prompt: '' }),
        ],
      }),
    ]);

    try {
      // Call GPT backend
      const res = await fetch('http://localhost:3000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: command }),
      });

      const data = await res.json();
      const reply = data.response || 'No response received.';

      // Print GPT response
      print([
        textLine({
          words: [textWord({ characters: 'GPT: ' + reply })],
        }),
      ]);
    } catch (err) {
      print([
        textLine({
          words: [
            textWord({
              characters: 'ERROR: Unable to reach GPT backend.',
            }),
          ],
        }),
      ]);
    }
  };

  return (
    <div style={{ width: '1000px', height: '600px', margin: 'auto' }}>
      <Terminal
        queue={eventQueue}
        banner={[textLine({ words: [textWord({ characters: bannerText })] })]}
        onCommand={handleCommand}
        prompt="> "
        effects={{
          pixels: true,
          scanner: true,
          screenEffects: true,
          textEffects: true,
        }}
        printer={{
          printerSpeed: 25,
          charactersPerTick: 4,
        }}
        loader={{
          slides: ['.', '..', '...'],
          loaderSpeed: 700,
        }}
      />
    </div>
  );
}
