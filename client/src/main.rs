fn main() {
    
    let mut a: String = String::from("a");

    let mut b: String = String::from("b");

    println!("a is {} and b is {}", a, b);

    a = String::from("c");
    b = String::from("d");

    println!("a is {} and b is {}", a, b);

    fn yoink(a: &String, b: &String) {
        println!("a is {} and b is {}", a, b);
    }

    yoink(&a, &b);
    println!("a is {} and b is {}", a, b);
    
    println!("Hello, world!");
}
