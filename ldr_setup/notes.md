apuntes y cosas sobre el sim . . . 
 
· desacoplar la asignación de puerto 
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

### coordenadas

* letras  → eje x
* numeros → eje y

coord_proto[5][2] = {
    {g, 2.5}  →  {7, 2.5},
    {i, 7.5}  →  {9, 7.5},
    {g, 14.5} →  {7, 14.5},
    {a, 6.5}  →  {1, 6.5},
    {c, 16.5} →  {3, 16.5}
} 

* WIDTH, HEIGHT (2D space) = 600, 600
* WIDTH, HEIGHT (proto)    = 10, 17

$ x_{space} = \frac{x_{proto} \times 600}{10}$
$ y_{space} = \frac{y_{proto} \times 600}{17}$

coord_space[5][2] = {
    {420, 88},   
    {540, 264},  
    {420, 511},  
    {60,  229},  
    {180, 582}   
};

### cosas

**Stand-By** (EMISOR == LOW): *agregado*
- cndo el emisor está apagado, shared_state["points"] conserva los últimos valores recibidos y la pantalla se queda congelada.
- enviar "STANDBY\n" para q se limpie shared_state["points"] = [] cuando alg == "STANDBY".

**puntos ocultos en 3CH**:  *agregado*
- cndo alg = "3CH" se sobreescribe la lista original, dps se itera sobre raw pero ya no existen

**rebote en PUSH (arduino):**
- una pulsación física puede generar rebotes → alg_i salte 2 algoritmos de golpe .. . . no me ha pasado pero si pasaa millis() < 50 ms 