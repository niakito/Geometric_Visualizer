// simulacion visualizador 

#include <LiquidCrystal.h>

const int PUSH   = 2 ;
const int EMISOR = 3 ;

const int LED[5] = {5, 6, 9, 10, 11} ;
const int LDR[5] = {A0, A1, A2, A3, A4} ;

const int coord[5][2] = {
    {420, 88},   
    {540, 264},  
    {420, 511},  
    {60,  229},  
    {180, 582}   
} ;
int weight[5] = {0, 0, 0, 0, 0} ;

// LDR reading 
const float GAMMA = 0.65 ; //  GL55XX (2~4 row)

float R_min = 1000000.0 ;  // res. en max. luz 
float R_max = 0.0       ;  // res. en max. sombra 

float lux_min = 0.0 ;
float lux_max = 1.0 ;
float lux_range = 1.0 ; 

// algorithm selection
const String ALG[3] = {
  "Convex Hull", 
  "Delaunay", 
  "Voronoi"
} ;

int alg_i = 0 ;
bool prev_state = LOW ;

// serial protocol
const unsigned long SEND_INTERVAL = 100 ; // 100 -- 10fps
unsigned long last_send = 0 ;

LiquidCrystal lcd_1(13, 12, 4, 7, 8, A5) ;

// función auxiliar
float get_R_ratio(int adc) {
  adc = constrain(adc, 1, 1022) ;
  return (1023.0 - (float)adc) / (float)adc ;
}

void setup()
{
  // inicializar lcd y comunicación serial
  lcd_1.begin(16, 2) ; 
  Serial.begin(9600) ;
  
  // calibración de la resistencia del LDR
  lcd_1.print("Calibrando...") ;
  
  while (millis() < 4000) {
    for (int i = 0 ; i < 5 ; i++ ) {
      int value = analogRead(LDR[i]) ;
      float r_ratio = get_R_ratio(value) ;

      if (r_ratio < R_min) R_min = r_ratio ; // luz → menor resistencia
      if (r_ratio > R_max) R_max = r_ratio ; // sombra → mayor resistencia
  	}
  }
  
  // valores por defecto
  if (R_min >= R_max) {
    R_min = get_R_ratio(969)  ; 
    R_max = get_R_ratio(49) ; 
  }

  lux_min = pow(R_max, -1.0 / GAMMA) ; // luz en sombra
  lux_max = pow(R_min, -1.0 / GAMMA) ; // luz en luz
  lux_range = lux_max - lux_min ; 
  
  // printear en el lcd los resultados de la calibración
  lcd_1.clear() ;
  
  lcd_1.setCursor(0, 0) ;
  lcd_1.print("R_min: ") ;
  lcd_1.print(R_min) ;
  
  lcd_1.setCursor(0, 1) ;
  lcd_1.print("R_max: ") ;
  lcd_1.print(R_max) ;
   
  unsigned long tiempo_inicio = millis();
  while (millis() - tiempo_inicio < 3000) {}

  // configurar pines
  pinMode(PUSH, INPUT)   ;
  pinMode(EMISOR, INPUT) ;
  for ( int i = 0 ; i < 5 ; i++ ) 
    pinMode(LED[i], OUTPUT)  ;
  
  lcd_1.clear() ;
}

void loop()
{
  bool lect = digitalRead(EMISOR) ;
  
  if (lect == HIGH) {
    // encendido
    lcd_1.setCursor(0, 0) ;
	lcd_1.print("(^. .^)/       ") ;
    
    lcd_1.setCursor(0, 1) ;
    lcd_1.print(ALG[alg_i] + "         ") ;

    bool push_state = digitalRead(PUSH) ;
    if (push_state == HIGH  && prev_state == LOW) alg_i = (alg_i + 1) % 3 ;
    prev_state = push_state ;
    
    for ( int i = 0 ; i < 5 ; i++ ){
      int raw = analogRead(LDR[i]) ;
      
      float R_curr = get_R_ratio(raw) ;
      R_curr = constrain(R_curr, R_min, R_max) ;
      
      float lux_actual = pow(R_curr, -1.0 / GAMMA) ;

      // normalización lineal → 0.0 = sombra ; 1.0 = luz
      float lineal_light = (lux_actual - lux_min) / lux_range ; // %luz/rango_luz
      lineal_light = constrain(lineal_light, 0.0, 1.0) ;
      int light = (int)(lineal_light * 1023.0) ;
    
      weight[i] = light ;
      analogWrite(LED[i], (int)(lineal_light * 255.0)) ;
    }
  	
    if (millis() - last_send >= SEND_INTERVAL) {
      last_send = millis() ;

      Serial.print(ALG[alg_i]) ;

      for (int i = 0; i < 5; i++) {
          Serial.print(";") ;
          Serial.print(coord[i][0]) ;
          Serial.print(",") ;
          Serial.print(coord[i][1]) ;
          Serial.print(",") ;
          Serial.print(weight[i]) ;
      }

      Serial.println() ;
    }

  }
  
  else {
    // apagado
    lcd_1.setCursor(0, 0) ;
    lcd_1.print("(^_  _^) Z z z  ") ;
    
    lcd_1.setCursor(0, 1) ;
    lcd_1.print("Stand-By        ") ;
    
    for ( int i = 0 ; i < 5 ; i++ )
      analogWrite(LED[i], 0) ;

    if (millis() - last_send >= SEND_INTERVAL) {
      last_send = millis() ;
      Serial.println("STANDBY;") ; 
    }
  }
}