export interface Question {
  text: string;
}

export interface Answer {
  answer: string;
}

export interface User {
      /**
     * User&apos;s identification number or string.
     */
    id?: number | string;
    /**
     * A user&apos;s name displayed in the chat.
     */
    name?: string;
    /**
     * An avatar URL.
     */
    avatarUrl?: string;
    /**
     * `alt` attribute for avatar image.
     */
    avatarAlt?: string;
}