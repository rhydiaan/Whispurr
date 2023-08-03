use std::io;
use num_derive::FromPrimitive;
use num_traits::FromPrimitive;

#[derive(FromPrimitive)]
enum Inputs{
    Invalid = 0,
    Login = 1,
    SignUp = 2,
}

fn main() {

    println!("Welcome to Whispurr! Please choose to either login or create a user. \nTo login please type \'1\' or to create a user please type \'2\' \n");
    
    let mut choice = String::new();

    io::stdin().read_line(&mut choice).expect("failed to readline");

    let trimmed_choice = choice.trim();

    if trimmed_choice.is_empty() {
        println!("Invalid input: Empty choice");
        return;
    }

    match FromPrimitive::from_u8(trimmed_choice.parse::<u8>().unwrap_or(0)) {
        Some(Inputs::Login) => {
            println!("You chose Login");
        }
        Some(Inputs::SignUp) => {
            println!("You chose Sign Up");
        }
        _ => {
            println!("Invalid choice");
            main();
        }
    }



    // match Choices {
    //     Choices::Login => login(),
    //     Choices::CreateUser => create_user(),
    //     _ => println!("Not a valid choice!")
    // }
}
