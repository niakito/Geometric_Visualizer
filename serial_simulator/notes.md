apuntes y cosas sobre el sim . . . 
 
· desacoplar la asignación de puerto 
· implementar y probar coloración de grafo
· implementar y probar teselación y delaunay con peso (prob solo radio de operación creoq lo demas es mui flojo)
̣· calibrar treshold y todoeso deps no necesitaría la blink sim

### tasa de baudios
- cuántas veces por segundo cambia la señal en un canal de comunicación
    - símbolos por segundo
    - símbolos → variación de voltaje, fase, frecuencia
- para comunicación entre dos dispositivos, ambos deben estar configurados a la misma velocidad de baudios

- estándares:
    - **9600 bd**: lenta pero estable y segura
    - **115 200 bd**: rápida, permite no saturar la comunicación cuando se envían muchos datos rápidamente (lecturas constantes de sensores)

- sincronización arduino&pc
    - **arduino**: Serial.begin(bd_rate)
    - **pc**: en monitor serie, esquina inferior derecha → menú desplegable

- rate para fotoresistencias: 9600 → los cambios de luz son lentos

### puertos de comunicación
- no usa tuberia como socat; arduino ya es un extremo
- comunicación en serie UART es estrictamente de uno a uno 
    - USB → canal directo
    - script ←_usb_→ COM2 ←_hw_→ arduino

- **linux**: (cmd) lsusb
- **ide**: esquina inferior derecha o tools > port