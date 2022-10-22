// PILA
fn pila_vacia(vect: &mut Vec<i64>) -> bool {
    return vect.len() == 0;
}

fn apilar(capacidad: usize, vect: &mut Vec<i64>, value: i64) {
    if vect.len() < capacidad {
        vect.insert(vect.len(), value);
    } else {
        println!("La pila ha llegado a su maxima capacidad");
    }
}

fn desapilar(vect: &mut Vec<i64>) -> i64 {
    if !pila_vacia(vect) {
        return vect.remove(vect.len()-1);
    } else {
        println!("La pila no tiene elementos");
    }
    return 0;
}

// COLA
fn cola_vacia(vect: &mut Vec<i64>) -> bool {
    return vect.len() == 0;
}

fn encolar(capacidad: usize, vect: &mut Vec<i64>, value: i64) {
    if vect.len() < capacidad {
        vect.push(value);
    } else {
        println!("La cola ha llegado a su maxima capacidad");
    }
}

fn desencolar(vect: &mut Vec<i64>) -> i64 {
    if !cola_vacia(vect) {
        return vect.remove(0);
    } else {
        println!("La cola no tiene elementos");
    }
    return 0;
}

fn main() {
    let capacidad: usize = 10;
    let mut pila: Vec<i64> = Vec::with_capacity(capacidad - 2);
    let mut cola: Vec<i64> = vec![1,2,3,4,5];

    let datos: [i64; 5] = [10,20,30,40,50];

    for dato in datos {
        apilar(capacidad, &mut pila, dato);
    }
    
    println!("{:?}", pila);
    println!("{}", desapilar(&mut pila));
    apilar(capacidad, &mut pila, 1250);
    apilar(capacidad, &mut pila, 2200);
    apilar(capacidad, &mut pila, 3500);
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{}", desapilar(&mut pila));
    println!("{:?}", pila);
    println!("Capacidad de pila");
    println!("{}", pila.capacity());
    println!("");

    encolar(capacidad, &mut cola, 800);
    println!("{:?}", cola);
    println!("{}", desencolar(&mut cola));
    encolar(capacidad, &mut cola, 1250);
    encolar(capacidad, &mut cola, 2200);
    encolar(capacidad, &mut cola, 3500);
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{}", desencolar(&mut cola));
    println!("{:?}", cola);
    println!("Capacidad de cola");
    println!("{}", cola.capacity());
    println!("");

    // vectores entre vectores
    let mut lista: Vec<Vec<i64>> = Vec::new();
    lista.push(vec![0; 10]);
    lista.push(vec![1; 10]);
    lista.push(vec![2; 10]);
    lista.push(vec![3; 10]);
    lista.push(vec![75,23,10,29,30,12,49,10,93]);
    println!("{:?}", lista);
    println!("");
    println!("{:?}", lista[0]);
    println!("{:?}", lista[1]);
    println!("{:?}", lista[2]);
    println!("{:?}", lista[3]);
    println!("{:?}", lista[4]);
    println!("{}", lista[4][8]);
    println!("");

    let vect = vec!["Hola", "!", "Sale", "Este", "Semestre", "2022"];
    println!("{}", vect.contains(&"Semestre") || vect.contains(&"2023"));
    println!("{}", vect.contains(&"Semestre") && vect.contains(&"2023"));
    println!("{}", vect.contains(&"Hola"));
}
