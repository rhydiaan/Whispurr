use std::io;
use num_derive::FromPrimitive;
use num_traits::FromPrimitive;
use url::Url;
use tungstenite::{connect, Message};

#[derive(FromPrimitive)]
enum Inputs{
    Invalid = 0,
    Login = 1,
    SignUp = 2,
}

struct User {
    username: String,
    password: String,
}



fn main() {

    println!("Welcome to Whispurr! Please choose to either login or create a user.");
    
    user_choice();

}


fn user_choice() {

    println!("To login please type \'1\' or to create a user please type \'2\' \n");

    let mut choice = String::new();

    io::stdin().read_line(&mut choice).expect("failed to readline");

    let trimmed_choice = choice.trim();

    if trimmed_choice.is_empty() {
        println!("\nInvalid input: Empty choice");
        return;
    }

    match FromPrimitive::from_u8(trimmed_choice.parse::<u8>().unwrap_or(0)) {
        Some(Inputs::Login) => {
            login(trimmed_choice);
        }
        Some(Inputs::SignUp) => {
            sign_up(trimmed_choice);
        }
        _ => {
            println!("Invalid choice");
            user_choice();
        }
    }
}

fn login(choice: &str) {

    println!("To login please type your username:");

    let mut username = String::new();

    io::stdin().read_line(&mut username).expect("failed to readline");

    let trimmed_username = username.trim();

    if trimmed_username.is_empty() {
        println!("\nInvalid input: Empty username");
        return;
    }

    println!("And now password:");

    let mut password = String::new();

    io::stdin().read_line(&mut password).expect("failed to readline");

    let trimmed_password = password.trim();

    if trimmed_password.is_empty() {
        println!("\nInvalid input: Empty password");
        return;
    }

    let user = User {
        username: String::from(trimmed_username),
        password: String::from(trimmed_password),
    };

    let (mut socket, _) = connect(
        Url::parse("wss://localhost:11000").unwrap()
    ).expect("Can't connect");
    println!("\nYou chose Login with the choice {}", choice);
    
    let message = format!(
        r#"{{
            "Login" : {{
                "id" : "{}",
                "password" : "{}"
            }}
        }}"#, user.username, user.password);
    

    let _ = socket.send(Message::Text(message));
    loop {
        let msg = socket.read().expect("Error reading message");
        println!("Received: {}", msg);
    }
    
}

fn sign_up(choice: &str) {

    println!("To create a user please type your username:");

    let mut username = String::new();

    io::stdin().read_line(&mut username).expect("failed to readline");

    let trimmed_username = username.trim();

    if trimmed_username.is_empty() {
        println!("\nInvalid input: Empty username");
        return;
    }

    println!("And now password:");

    let mut password = String::new();

    io::stdin().read_line(&mut password).expect("failed to readline");

    let trimmed_password = password.trim();

    if trimmed_password.is_empty() {
        println!("\nInvalid input: Empty password");
        return;
    }

    let user = User {
        username: String::from(trimmed_username),
        password: String::from(trimmed_password),
    };


    let (mut socket, _) = connect(
        Url::parse("wss://localhost:11000").unwrap()
    ).expect("Can't connect");
    println!("\nYou chose Sign Up with the choice {}", choice);
    
    let message = format!(
        r#"{{
            "CreateUser" : {{
                "id" : "{}",
                "password" : "{}"
            }}
        }}"#, user.username, user.password);
    

    let _ = socket.send(Message::Text(message));
    loop {
        let msg = socket.read().expect("Error reading message");
        println!("Received: {}", msg);
    }
    
}


// {
// 	"Login" : {
// 		"id" : "user_id",
// 		"password" : "password"
// 	}
// }

// {
// 	"SendMessage" : {
// 		"message" : "Hello world!",
// 		"target" : "target_id"
// 	},
// 	"id" : "sender_id"
// }