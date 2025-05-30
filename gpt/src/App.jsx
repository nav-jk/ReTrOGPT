// App.js
import './App.css';
import { useEffect, useState } from 'react';
import RetroTerminal from './components/RetroTerminal';

function WelcomeScreen({ onStart }) {
  const fullText = "*** WELCOME TO GPT-2 TERMINAL ***\nPRESS 'START' TO BEGIN";
  const [displayedText, setDisplayedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index < fullText.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(fullText.slice(0, index + 1));
        setIndex(index + 1);
      }, 50);
      return () => clearTimeout(timeout);
    }
  }, [index]);

  return (
    <div className="terminal-content">
      <pre className="typewriter">{displayedText}<span className="cursor" /></pre>
      {index === fullText.length && (
        <button onClick={onStart} className="start-button">START</button>
      )}
    </div>
  );
}

function App() {
  const [started, setStarted] = useState(false);
  const [displayLines, setDisplayLines] = useState([]);
  const [bootComplete, setBootComplete] = useState(false);

  useEffect(() => {
    if (started) {
      const bootMessages = [
        '(C) 1991 Motherboard, Inc.',
        'BIOS Date: 09/29/91 15:43:29 Ver: 08.00.15',
        'CPU: Intel(R) CPU 330 @ 640 MHz',
        'Speed: 640 MHz',
        'This VGA/PCI Bios is released under the GNU LGPL',
        '',
        'Press F11 for BIOS POPUP',
        'Memory Clock: 64 MHz, Tcl:7 Trcd:4 Trp:8 Tras:20 (2T Timing) 8 bit',
        'Memory Test: 128420K OK',
        '',
        'PNP ROM Version: 9303',
        'NVMM ROM Version: 4.092.88',
        'Initializing USB Controllers.. Done.',
        '128MB OK',
        'USB Device(s): 1 Keyboard, 1 Mouse, 1 Hub, 1 Storage Device',
        'Auto-detecting USB Mass Storage Devices..',
        'Device #01: USB 2.0 Flashdisk "Speed"',
        '01 USB mass storage devices found and configured.',
        '(C) Motherboard, Inc.',
        '64-0100-00001-01001111-092909-79297-1AE0V003-Y2UC',
        'Booting from Hard Disk...',
        'C:\\>'
      ];

      let currentLine = 0;
      const interval = setInterval(() => {
        setDisplayLines(prev => [...prev, bootMessages[currentLine]]);
        currentLine++;
        if (currentLine >= bootMessages.length) {
          clearInterval(interval);
          setBootComplete(true);
        }
      }, 500);

      return () => clearInterval(interval);
    }
  }, [started]);

  useEffect(() => {
    if (bootComplete) {
      const beep = new Audio('/sounds/beep.mp3');
      beep.volume = 0.5;
      beep.play().catch(err => {
        console.warn("Autoplay failed (user interaction needed):", err);
      });
    }
  }, [bootComplete]);

  const handleKeyPress = () => {
    if (bootComplete) {
      setStarted(true);  // This will ensure the terminal gets shown
    }
  };

  useEffect(() => {
    if (bootComplete) {
      window.addEventListener('keydown', handleKeyPress);
    }
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [bootComplete]);

  return (
    <div className="background-section">
      <div className="terminal-overlay">
        {!started ? (
          <WelcomeScreen onStart={() => setStarted(true)} />
        ) : !bootComplete ? (
          <div className="bios-screen">
            <pre className="bios-text">
              {displayLines.map((line, idx) => <div key={idx}>{line}</div>)}
            </pre>
          </div>
        ) : (
          <RetroTerminal />  // This will stay persistent after the boot sequence
        )}
      </div>
    </div>
  );
}

export default App;
