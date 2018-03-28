//
//  ViewController.swift
//  City Data iOS
//
//  Created by Mohammed Guniem on 28.03.2018.
//  Copyright © 2018 University of Stavanger. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    // Refers to the web frame element from Main.storyboard
    @IBOutlet weak var webview: UIWebView!
   
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let url = URL(string: "https://www.google.no/")
        let urlRequest = URLRequest(url: url!)
        
        webview.loadRequest(urlRequest)
        
    }


}

