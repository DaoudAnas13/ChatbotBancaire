import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { User } from './constants';
import { Observable } from 'rxjs';

interface Message {
  text: string;
  userId: number;
  sender: string;
  date: Date;
  isLoading?:boolean;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent {
  messages: Message[] = [];
  currentUser = { id: 1, name: 'You' };  // You as the user
  botUser = { id: 2, name: 'Bot' };
  regenerationText = "Regeneration...";

    loadingText = 'Loading';  // Text to display for loading
  loadingDots = '';         // Dots animation string
  loadingInterval?: any;    // To keep interval reference

  constructor(private http: HttpClient) {}

    startLoadingAnimation() {
    let count = 0;
    this.loadingDots = '';
    this.loadingInterval = setInterval(() => {
      count = (count + 1) % 4; // cycle 0..3 dots
      this.loadingDots = '.'.repeat(count);
    }, 500);
  }

  stopLoadingAnimation() {
    if (this.loadingInterval) {
      clearInterval(this.loadingInterval);
      this.loadingDots = '';
    }
  }

  onTest(e:any):void{
    console.log("EEEEEEEEEE") 
    console.log(e.message.text) 
  }

onSendMessage(e: any): void {
  // Add loading message from bot
  const loadingMessage: Message = {
    text: '',       // start empty, no dots now (or keep '...' if you want)
    userId: this.botUser.id,
    sender: this.botUser.name,
    date: new Date(),
    isLoading: true
  };

  this.messages = [...this.messages, loadingMessage];
  this.startLoadingAnimation();

  this.http.post<{ answer: string }>('http://localhost:8000/ask', { text: e.message.text })
    .subscribe({
      next: (response) => {
        this.stopLoadingAnimation();

        // Get the index of the loading message in the array
        const loadingMsgIndex = this.messages.findIndex(msg => msg.isLoading);

        if (loadingMsgIndex === -1) return;

        let currentText = '';
        let charIndex = 0;
        const fullText = response.answer;

        // Replace loading message with empty text (or initial text)
        this.messages[loadingMsgIndex].text = '';
        this.messages[loadingMsgIndex].isLoading = false;

        // Start typing simulation
        const typingInterval = setInterval(() => {
          if (charIndex < fullText.length) {
            currentText += fullText.charAt(charIndex);
            charIndex++;

            // Update message text
            this.messages[loadingMsgIndex].text = currentText;

            // Trigger change detection by creating new array reference
            this.messages = [...this.messages];
          } else {
            // Done typing, clear interval
            clearInterval(typingInterval);
          }
        }, 20); // 50ms per character (adjust speed here)
      },
      error: () => {
        this.stopLoadingAnimation();

        // Remove loading message
        this.messages = this.messages.filter(msg => !msg.isLoading);

        // Add error message
        const errorMsg: Message = {
          text: 'Error retrieving response from server.',
          userId: this.botUser.id,
          sender: this.botUser.name,
          date: new Date(),
        };
        this.messages = [...this.messages, errorMsg];
      }
    });
}


}