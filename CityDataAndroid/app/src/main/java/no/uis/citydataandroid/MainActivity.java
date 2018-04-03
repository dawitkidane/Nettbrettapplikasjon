package no.uis.citydataandroid;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends AppCompatActivity {

    private WebView Web_View;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Capturing the Web View element from the XML sheet file, activity_mail.xml.
        Web_View = (WebView) findViewById(R.id.WebView);

        // This line is to enable loading the website inside the app and not in the default
        // external browser of the users device.
        Web_View.setWebViewClient(new WebViewClient());

        // Specifies which website will be loaded in the web view element box.
        Web_View.loadUrl("http://www.google.no/");

        // enables JavaScript
        WebSettings webSettings = Web_View.getSettings();
        webSettings.setJavaScriptEnabled(true);


    }

    // event that listens to the back button on the user android device
    @Override
    public void onBackPressed() {
        // if the history includes at least one page, then go to the last visited page
        if (Web_View.canGoBack()) {
            Web_View.goBack();

        // if not, then close/hide the App
        } else {
            super.onBackPressed();
        }
    }
}
