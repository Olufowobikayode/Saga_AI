// file: frontend/src/components/EmailForm.js
import React from 'react';
import { useForm, ValidationError } from '@formspree/react';
import { toast } from 'react-hot-toast';
import { Send } from 'lucide-react';

function EmailForm() {
  // IMPORTANT: Replace 'YOUR_FORM_ID' with your actual Formspree form ID
  const [state, handleSubmit] = useForm("YOUR_FORM_ID");

  if (state.succeeded) {
    toast.success('Thanks for your message! We will get back to you soon.');
    return <p className="text-center font-semibold text-green-600">Message sent successfully!</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Your Email
        </label>
        <input
          id="email"
          type="email"
          name="email"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
        <ValidationError prefix="Email" field="email" errors={state.errors} className="mt-2 text-sm text-red-600" />
      </div>
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows="4"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
        <ValidationError prefix="Message" field="message" errors={state.errors} className="mt-2 text-sm text-red-600" />
      </div>
      <button type="submit" disabled={state.submitting} className="w-full flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400 transition-colors">
        <Send size={18} />
        {state.submitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}

export default EmailForm;