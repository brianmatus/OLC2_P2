fn main() {
    let mut placa_: &str = "default";

    let mut x = 2002;
    match x {
        // 1 | 2 | 3 estas son coincidencias
        2000 | 2001 | 2002 => {
            placa_ = "Caso1";
        }
        2003 | 2004 | 2005 => placa_ = "Caso2",
        2006 =>  placa_ = "Caso3",
        _ => println!("Caso Default")
    }

    println!("placa:{}", placa_);
}