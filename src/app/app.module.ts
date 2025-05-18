import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { DxButtonModule, DxChatModule } from 'devextreme-angular';

import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule,
    DxButtonModule,
    HttpClientModule, // for HTTP calls
    DxChatModule // import DevExtreme Chat
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}